#!/usr/bin/python3
#
#            ECG Viewer
#   Written by Kevin Williams - 2022
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

# String used in the title-bar and about window
VERSION = "v2.0.0-b.2"

import os
import sys
import math
import time
import serial
import numpy
import platform
import pyqtgraph as pg
import statistics as stat

# import locals
import images_qr
from PyQt5 import QtWidgets, uic, QtCore, QtWidgets
from pyqtgraph import PlotWidget
from debug import debug_timer
from ecg_viewer_window import Ui_MainWindow
from about import Ui_about_window

# manual includes to fix occasional compile problem
from ecg_viewer_window import Ui_MainWindow
from pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5 import *
from pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5 import *
from pyqtgraph.imageview.ImageViewTemplate_pyqt5 import *
from pyqtgraph.console.template_pyqt5 import *

# About window. The class is so tiny it might as well be defined here.
class AboutWindow(QtWidgets.QDialog, Ui_about_window):
    def __init__(self, *args, **kwargs):
        super(AboutWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.version.setText(VERSION)
        self.icon.setPixmap(QtGui.QPixmap(":/icon/icon.png"))
        self.setWindowIcon(QtGui.QIcon(':/icon/icon.png'))


class ECGViewer(QtWidgets.QMainWindow, Ui_MainWindow):

    # import class methods
    from _ecg_serial_handler import com_connect, com_refresh, get_input, start_capture_timer, \
        stop_capture_timer, com_check_device, do_calibrate
    from _ecg_grapher import draw_graph, graph_fit, bold_toggle, restart_graph_timer, \
        stop_graph_timer, start_graph_timer
    from _ecg_math import detect_peaks, update_hr
    from _ecg_ui_handler import alarm_on, alarm_off, set_message, clear_message, force_invert, \
        run_toggle, export_data_raw, export_data_png, export_data_csv, show_about, display_error_message

    def __init__(self, *args, **kwargs):
        super(ECGViewer, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.about_window = AboutWindow()
        self.graph.disableAutoRange()
        self.setWindowTitle("DIYECG Viewer - " + VERSION)
        self.setWindowIcon(QtGui.QIcon(':/icon/icon.png'))

        # Capture timer
        self.capture_timer = QtCore.QTimer()
        self.capture_timer.timeout.connect(self.do_update)
        self.capture_rate_ms = 0
        self.capture_timer_qt = QtCore.QElapsedTimer()
        self.capture_index = 0

        # graph timer
        self.graph_timer = QtCore.QTimer()
        self.graph_timer.timeout.connect(self.draw_graph)
        self.graph_frame_rate = 30                                 # change to adjust refresh rate
        self.graph_timer_ms = int(1 / (self.graph_frame_rate / 1000))

        # set menu option metadata
        self.action30_FPS.setData(30)
        self.action15_FPS.setData(15)
        self.action8_FPS.setData(8)

        # Connect buttons to methods
        self.button_refresh.clicked.connect(self.com_refresh)
        self.button_connect.clicked.connect(self.connect_toggle)
        self.button_reset.clicked.connect(self.reset)
        self.button_run.clicked.connect(self.run_toggle)
        self.button_force_invert.clicked.connect(self.force_invert)
        self.graph_zoom_slider.sliderReleased.connect(self.graph_fit)
        self.show_track.stateChanged.connect(self.reset)
        self.FPSGroup.triggered.connect(self.restart_graph_timer)
        self.button_run.setDisabled(True)
        self.actionBold_Line.toggled.connect(self.bold_toggle)
        self.actionRAW.triggered.connect(self.export_data_raw)
        self.actionPNG.triggered.connect(self.export_data_png)
        self.actionCSV.triggered.connect(self.export_data_csv)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionQuit.triggered.connect(sys.exit)

        # set tooltips
        self.holdoff_box.setToolTip("Time to wait until it detects the next peak. Set higher if the heart rate triggers too quickly.")
        self.prominence_box.setToolTip("The expected magnitude of the peaks. Lower to increase sensitivity.")
        self.button_force_invert.setToolTip("Inverts the waveform. Useful if calibration didn't automatically invert the signal.")
        self.show_track.setToolTip("Show the real-time peak detection. Disables filtering while on")
        self.button_reset.setToolTip("Clears graph data. Forces recalibration.")
        self.button_run.setToolTip("Pauses data capture.")
        self.button_refresh.setToolTip("Refresh the list of connected devices.")
        self.button_connect.setToolTip("Connected to the selected device.")
        self.graph_zoom_slider.setToolTip("Changes the vertical zoom of the graph.")
        self.window_length_box.setToolTip("Higher values give more consistent filtering, but increases bias error. VALUE MUST BE ODD.")
        self.polyorder_box.setToolTip("Determines the 'complexity' of the filtering applied. Higher values retain more resolution.")
        self.actionBold_Line.setToolTip("Draws graph with thicker line. Reduces visual accuracy. Slower.")

        # Serial Variables
        self.ser: serial.Serial = serial.Serial(baudrate = 115200)

        # data variables
        self.current_reading = 0
        self.value_history_max = 5000
        self.value_history = numpy.zeros(self.value_history_max)
        self.time_history  = numpy.zeros(self.value_history_max)
        self.invert_modifier = 1
        self.calibrating = self.value_history_max
        self.peaks = list()

        # graph properties
        self.graph.showGrid(True, True, alpha = 0.5)
        self.graph_padding_factor = 0.667
        self.green_pen = pg.mkPen('g', width = 2)
        self.red_pen = pg.mkPen('r', width = 2)
        self.yellow_pen = pg.mkPen('y')

        # ecg rate alarm limits
        self.rate_alarm_max = 120
        self.rate_alarm_min = 40
        self.rate_alarm_history = [80] * 3
        self.rate_alarm_active = False

        # perform initial reset
        self.reset()
        self.com_refresh()


    def do_update(self) -> None:
        """
        Main update loop for ECG Reader. Called via timer.
        """

        # fetches a new reading from the Arduino, stores in value_history and time_history
        reading_ok = self.get_input()

        # Run the calibration routine. self.calibrating is a timer that runs until its value is -1
        if(self.calibrating > -1 and reading_ok):
            self.do_calibrate()     # only add reading to calibration if it was valid

        # if we've reached a full sample period, self.capture_index will roll-over back
        # to zero. When this happens, fit the graph, find peaks, and update the heart rate
        if(self.capture_index == 0 and reading_ok):
            self.ser.reset_input_buffer()
            self.graph_fit()
            self.detect_peaks()
            self.update_hr()


    def reset(self) -> None:
        """
        Resets all record history and calibration. Clears graph.
        """

        self.graph.clear()
        self.curve = self.graph.plot(numpy.arange(self.value_history.size), self.value_history, pen = self.green_pen, skipFiniteCheck = True)
        self.capture_index = 0
        self.alarm_off()
        self.rate_alarm_active = False
        self.calibrating = self.value_history_max + 1
        self.value_history = numpy.zeros(self.value_history_max)
        self.time_history  = numpy.zeros(self.value_history_max)


    def connect_toggle(self) -> None:
        """
        Connect/Disconnect from the serial device selected in the dropdown menu.\n
        This function should be called from the UI.
        """

        if not self.ser.isOpen():
            if self.com_connect():
                self.button_refresh.setDisabled(True)
                self.button_run.setDisabled(False)
                self.button_connect.setText("Disconnect")
                self.invert_modifier = 1
                self.reset()
                self.start_capture_timer()
        else:
            self.stop_capture_timer()
            self.ser.close()
            self.button_refresh.setDisabled(False)
            self.button_run.setDisabled(True)
            self.button_connect.setText("Connect")
            self.com_refresh()

@debug_timer
def check_resolution(app: QtWidgets.QApplication) -> None:
    """
    Checks the resolution to make sure it meets or exceeds the reccomended size.\n
    Displays a message to the user\n
    Does not prevent the program from running if the resolution is too low.
    """

    screen = app.primaryScreen().size()
    size_string = str(screen.width()) + " x " + str(screen.height())
    print("Detected resolution: " + size_string)
    if(screen.width() < 1024 or screen.height() < 768):
        error_message = QtWidgets.QMessageBox()
        error_message.setWindowTitle("Notice")
        error_message.setText("The reccomended minimum display resolution is 1024x768.\n\nYour resolution: " + size_string)
        error_message.exec_()


def print_sys_info() -> None:
    """Prints system information to console."""
    print(VERSION)
    print(time.ctime())
    print(platform.platform())
    print("Python Version: " + platform.python_version())
    print("Directory: " + os.getcwd())
    print('-' * 80)


def main():
    print_sys_info()
    app = QtWidgets.QApplication(sys.argv)
    main = ECGViewer()
    main.show()
    check_resolution(app)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

