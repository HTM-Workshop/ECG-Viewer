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

import os
import sys
import time
import platform
import serial
import numpy
import logging
import pyqtgraph as pg
from webbrowser import Error as wb_error
from webbrowser import open as wb_open
from PyQt5 import QtWidgets, QtCore, QtGui

# manual includes to fix occasional compile problem
from pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5 import *
from pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5 import *
from pyqtgraph.imageview.ImageViewTemplate_pyqt5 import *
from pyqtgraph.console.template_pyqt5 import *

# import locals
from debug import debug_timer
from ecg_viewer_window import Ui_MainWindow
from about import Ui_about_window
from license import Ui_license_window
import images_qr        # required for icon to work properly


# String used in the title-bar and about window
VERSION = "v2.2.0"


# About window. The class is so tiny it might as well be defined here.
class AboutWindow(QtWidgets.QDialog, Ui_about_window):
    """
    About dialog box window.
    """

    def __init__(self, *args, **kwargs):
        super(AboutWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.version.setText(VERSION)
        self.icon.setPixmap(QtGui.QPixmap(":/icon/icon.png"))
        self.setWindowIcon(QtGui.QIcon(':/icon/icon.png'))


# Same for license window
class LicenseWindow(QtWidgets.QDialog, Ui_license_window):
    """
    License dialog box window.
    """

    def __init__(self, *args, **kwargs):
        super(LicenseWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(':/icon/icon.png'))


class ECGViewer(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    Main class for the ECG Viewer application.
    """

    # import class methods
    from _ecg_serial_handler import ser_com_connect, ser_com_refresh, ser_get_input, ser_start_capture_timer, \
        ser_stop_capture_timer, ser_check_device, ser_do_calibrate
    from _ecg_grapher import graph_draw, graph_fit, graph_bold_toggle, graph_restart_timer, \
        graph_stop_timer, graph_start_timer
    from _ecg_math import math_detect_peaks, math_calc_hr, math_calc_sps
    from _ecg_ui_handler import ui_alarm_on, ui_alarm_off, ui_set_message, ui_clear_message, ui_force_invert, \
        ui_run_toggle, ui_export_data_raw, ui_export_data_png, ui_export_data_csv, ui_show_about, \
        ui_display_error_message, ui_set_tooltips, ui_statusbar_message, ui_holdoff_box_update, ui_show_license

    def __init__(self, *args, **kwargs):
        super(ECGViewer, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.about_window = AboutWindow()
        self.license_window = LicenseWindow()
        self.graph.disableAutoRange()
        self.setWindowTitle("ECG Viewer - " + VERSION)
        self.setWindowIcon(QtGui.QIcon(':/icon/icon.png'))

        # Capture timer
        self.capture_timer = QtCore.QTimer()
        self.capture_timer.timeout.connect(self.do_update)
        self.capture_rate_ms = 0
        self.capture_timer_qt = QtCore.QElapsedTimer()
        self.capture_index = 0

        # graph timer
        self.graph_timer = QtCore.QTimer()
        self.graph_timer.timeout.connect(self.graph_draw)
        self.graph_frame_rate = 30
        self.graph_timer_ms = int(1 / (self.graph_frame_rate / 1000))

        # set FPS menu option metadata
        self.action30_FPS.setData(30)
        self.action15_FPS.setData(15)
        self.action8_FPS.setData(8)

        # set Window Size menu option metadata
        self.action2000.setData(2000)
        self.action5000.setData(5000)
        self.action8000.setData(8000)
        self.action10000.setData(10000)

        # Connect buttons to methods
        self.button_refresh.clicked.connect(self.ser_com_refresh)
        self.button_connect.clicked.connect(self.connect_toggle)
        self.button_reset.clicked.connect(self.reset)
        self.button_run.clicked.connect(self.ui_run_toggle)
        self.button_ui_force_invert.clicked.connect(self.ui_force_invert)
        self.graph_zoom_slider.sliderReleased.connect(self.graph_fit)
        self.show_track.stateChanged.connect(self.reset)
        self.FPSGroup.triggered.connect(self.graph_restart_timer)
        self.button_run.setDisabled(True)
        self.actionBold_Line.toggled.connect(self.graph_bold_toggle)
        self.actionRAW.triggered.connect(self.ui_export_data_raw)
        self.actionPNG.triggered.connect(self.ui_export_data_png)
        self.actionCSV.triggered.connect(self.ui_export_data_csv)
        self.actionAbout.triggered.connect(self.ui_show_about)
        self.actionLicense.triggered.connect(self.ui_show_license)
        self.actionGet_Source_Code.triggered.connect(self.open_source_code_webpage)
        self.actionQuit.triggered.connect(sys.exit)
        self.WindowSizeGroup.triggered.connect(self.window_size_update)
        self.actionStart_Stop.triggered.connect(self.ui_run_toggle)
        self.actionStart_Stop.setDisabled(True)
        self.actionReset.triggered.connect(self.reset)
        self.actionAuto_Holdoff.triggered.connect(self.ui_holdoff_box_update)

        # set tooltips
        self.ui_set_tooltips()

        # Serial Variables
        self.ser: serial.Serial = serial.Serial(baudrate = 115200)

        # data variables
        self.current_reading = 0
        self.value_history_max = 8000
        self.value_history = numpy.zeros(self.value_history_max)
        self.time_history  = numpy.zeros(self.value_history_max)
        self.invert_modifier = 1
        self.calibrating = self.value_history_max
        self.peaks = list()
        self.holdoff_factor = 0.31

        # graph properties
        self.graph.showGrid(True, True, alpha = 0.5)
        self.graph_padding_factor = 0.667
        self.green_pen = pg.mkPen('g', width = 2)
        self.red_pen = pg.mkPen('r', width = 2)
        self.yellow_pen = pg.mkPen('y')

        # ecg rate average
        self.rate_history = [80] * 3

        # ecg rate alarm limits
        self.rate_alarm_max = 120
        self.rate_alarm_min = 40
        self.rate_alarm_active = False

        # perform initial reset
        self.reset()
        self.ser_com_refresh()

    def open_source_code_webpage(self):
        """
        Opens a link to the project source code.
        """
        try:
            wb_open("https://github.com/HTM-Workshop/ECG-Viewer", autoraise = True)
        except wb_error as error:
            error_msg = "Could not open URL.\n\n" + error
            logging.warning(error_msg)
            self.ui_display_error_message("Open URL Error", error_msg)


    def do_update(self) -> None:
        """
        Main update loop for ECG Reader. Called via timer.
        """

        # fetches a new reading from the Arduino, stores in value_history and time_history
        reading_ok = self.ser_get_input()

        # Run the calibration routine. self.calibrating is a timer that runs until its value is -1
        if(self.calibrating > -1 and reading_ok):
            self.ser_do_calibrate()     # only add reading to calibration if it was valid

        # if we've reached a full sample period, self.capture_index will roll-over back
        # to zero. When this happens, fit the graph, find peaks, and update the heart rate
        if(self.capture_index == 0 and reading_ok):
            self.ser.reset_input_buffer()
            sps = self.math_calc_sps()
            if self.actionAuto_Holdoff.isChecked():
                holdoff = round(sps * self.holdoff_factor)
                self.holdoff_box.setValue(holdoff)
            self.graph_fit()
            self.math_detect_peaks()
            inst_rate, avg_rate = self.math_calc_hr()
            self.update_hr(inst_rate, avg_rate)
            self.ui_statusbar_message(f"Samples per second: {sps}")


    def update_hr(self, inst_rate: int, avg_rate: int) -> None:
        """
        Updates the UI elements/alarms using the provided heart rate information.
        """
        
        if inst_rate > 0:
            if self.actionBPM_Averaging.isChecked():
                self.lcdNumber.display(avg_rate)
            else:
                self.lcdNumber.display(inst_rate)
            self.ui_clear_message()
            if avg_rate > self.high_limit_box.value():
                self.rate_alarm_active = True
                self.ui_alarm_on("MAX RATE ALARM")
            if self.low_limit_box.value() > avg_rate:
                self.rate_alarm_active = True
                self.ui_alarm_on("MIN RATE ALARM")
            if self.rate_alarm_active:
                if(avg_rate <= self.high_limit_box.value() and self.low_limit_box.value() <= avg_rate):
                    self.rate_alarm_active = False
                    self.ui_alarm_off()            
        else:
            self.lcdNumber.display(0)
            self.ui_set_message("SIGNAL LOSS")


    def reset(self) -> None:
        """
        Resets all record history and calibration. Clears graph.
        """

        self.graph.clear()
        self.curve = self.graph.plot(numpy.arange(self.value_history.size), self.value_history, pen = self.green_pen, skipFiniteCheck = True)
        self.capture_index = 0
        self.ui_alarm_off()
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
            if self.ser_com_connect():
                self.button_refresh.setDisabled(True)
                self.button_run.setDisabled(False)
                self.actionStart_Stop.setDisabled(False)
                self.button_connect.setText("Disconnect")
                self.invert_modifier = 1
                self.reset()
                self.ser_start_capture_timer()
        else:
            self.ser_stop_capture_timer()
            self.ser.close()
            self.button_refresh.setDisabled(False)
            self.button_run.setDisabled(True)
            self.actionStart_Stop.setDisabled(True)
            self.button_connect.setText("Connect")
            self.ser_com_refresh()
    
    def window_size_update(self):
        """
        Updates value_history_max size based on the selection from the UI. Calls
        reset on exit to resize/redraw the graph to fit the new window size.
        """

        self.value_history_max = self.WindowSizeGroup.checkedAction().data()
        self.graph_fit()
        self.reset()

@debug_timer
def check_resolution(app: QtWidgets.QApplication) -> None:
    """
    Checks the resolution to make sure it meets or exceeds the reccomended size.\n
    Displays a message to the user\n
    Does not prevent the program from running if the resolution is too low.
    """

    screen = app.primaryScreen().size()
    size_string = f"{screen.width()}x{screen.height()}"
    logging.info(f"Detected resolution: {size_string}")
    if(screen.width() < 1024 or screen.height() < 768):
        error_message = QtWidgets.QMessageBox()
        error_message.setWindowTitle("Notice")
        error_message.setText("The reccomended minimum display resolution is 1024x768.\n\nYour resolution: " + size_string)
        error_message.exec_()


def log_sys_info() -> None:
    """Logs system info."""
    logging.info(f"Build: {VERSION}")
    logging.info(time.ctime())
    logging.info(platform.platform())
    logging.info(f"Python Version: {platform.python_version()}")
    logging.info(f"Directory: {os.getcwd()}")


def main():
    """
    Main Function.
    Starts logging system and GUI.
    Passes control to the ECGViewer class. 
    """

    # Init logging and get system info
    start_time = time.time()
    lfmt = "%(levelname)s [%(funcName)s]: %(message)s"
    try:
        # When compiled as .app file on Mac, sandboxing will have the logical working directory '/'
        # meaning creating logfiles in the same directory will fail. We'll need to redirect the 
        # log output to the standard logfile location for user apps.
        if sys.platform == 'darwin':
            log_dir = os.path.expanduser('~/Library/Logs/')
            log_path = log_dir + "ecg_viewer.log"
            logging.basicConfig(filename=log_path, level=logging.INFO, filemode='w', format=lfmt)
        else:
            logging.basicConfig(filename='ecg_viewer.log', level=logging.INFO, filemode='w', format=lfmt)
    except OSError as e:
        logging.basicConfig(level=logging.INFO, format=lfmt)
        logging.error(e)
    logging.info("PROGRAM START")
    log_sys_info()

    # start program
    app = QtWidgets.QApplication(sys.argv)
    main_app = ECGViewer()
    main_app.show()
    check_resolution(app)
    ret = app.exec_()       # main loop call
    
    # Close program
    logging.info("PROGRAM EXIT")
    logging.info(f"Runtime: {time.time() - start_time}")
    logging.shutdown()
    sys.exit(ret)


if __name__ == '__main__':
    main()