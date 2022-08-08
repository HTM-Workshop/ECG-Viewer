#!/usr/bin/python3


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
#  

VERSION = "v1.1.0"
from PyQt5 import QtWidgets, uic, QtCore, QtWidgets
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import statistics as stat
import sys, os, math, serial, time, platform, numpy
from ecg_viewer_window import Ui_MainWindow
import images_qr

# manual includes to fix occasional compile problem
from ecg_viewer_window import Ui_MainWindow 
from pyqtgraph.graphicsItems.ViewBox.axisCtrlTemplate_pyqt5 import *  
from pyqtgraph.graphicsItems.PlotItem.plotConfigTemplate_pyqt5 import *  
from pyqtgraph.imageview.ImageViewTemplate_pyqt5 import *  
from pyqtgraph.console.template_pyqt5 import * 

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.graph.disableAutoRange()    
        self.setWindowTitle("DIYECG Viewer - " + VERSION)
        self.setWindowIcon(QtGui.QIcon(':/icon/icon.png'))
        
        # Capture timer
        self.capture_timer = QtCore.QTimer()
        self.capture_timer.timeout.connect(self.do_update)
        self.capture_rate_ms = 1
        self.capture_timer_qt = QtCore.QElapsedTimer()
        self.capture_index = 0
        
        # graph timer
        self.graph_timer = QtCore.QTimer()
        self.graph_timer.timeout.connect(self.draw_graph)
        self.graph_frame_rate = 15                                 # change to adjust refresh rate
        self.graph_timer_ms = int(1 / (self.graph_frame_rate / 1000))
        
        # Connect buttons to methods
        self.button_refresh.clicked.connect(self.com_refresh)
        self.button_connect.clicked.connect(self.com_connect)  
        self.button_reset.clicked.connect(self.reset)
        self.button_run.clicked.connect(self.run_toggle)
        self.button_export.clicked.connect(self.export_data)
        self.button_force_invert.clicked.connect(self.force_invert)
        self.graph_zoom_slider.sliderReleased.connect(self.graph_fit)
        self.bold_checkBox.stateChanged.connect(self.bold_toggle)
        self.button_run.setDisabled(True)
        
        # set tooltips
        self.holdoff_box.setToolTip("Time to wait until it detects the next peak. Set higher if the heart rate triggers too quickly.")
        self.prominence_box.setToolTip("The expected magnitude of the peaks. Lower to increase sensitivity.")
        self.button_force_invert.setToolTip("Inverts the waveform. Useful if calibration didn't automatically invert the signal.")
        self.show_track.setToolTip("Show the real-time peak detection. Disables filtering while on")
        self.button_reset.setToolTip("Clears graph data. Forces recalibration.")
        self.button_run.setToolTip("Pauses data capture.")
        self.button_export.setToolTip("Export the displayed waveform as a raw binary file.")
        self.button_refresh.setToolTip("Refresh the list of connected devices.")
        self.button_connect.setToolTip("Connected to the selected device.")
        self.graph_zoom_slider.setToolTip("Changes the vertical zoom of the graph.")
        self.window_length_box.setToolTip("Higher values give more consistent filtering, but increases bias error. VALUE MUST BE ODD.")
        self.polyorder_box.setToolTip("Determines the 'complexity' of the filtering applied. Higher values retain more resolution.")
        self.bold_checkBox.setToolTip("Draws graph with thicker line. Reduces visual accuracy.")
        
        # connection status
        self.ser = None
        self.com_port = ''

        # perform initial com port check
        self.com_refresh()  
        
        # data variables
        self.current_reading = 0
        self.value_history_max = 2500
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
        
        # run state
        self.run = True

        # ecg rate alarm limits
        self.rate_alarm_max = 120
        self.rate_alarm_min = 40
        self.rate_alarm_history = [80] * 3
        self.rate_alarm_active = False
        
        # perform initial reset
        self.reset()

    # import class methods
    from ecg_serial_handler import com_connect, com_refresh, get_input
    from ecg_grapher import draw_graph, graph_fit, bold_toggle
    from ecg_math import detect_peaks, update_hr
    from ecg_ui_handler import alarm_on, alarm_off, set_message, clear_message, force_invert, run_toggle, export_data
    
    # main update loop
    def do_update(self):
        self.get_input()
        if(self.capture_index == 0 and self.calibrating == -1):
            self.graph_fit()
            self.update_hr()
            
    # resets all history, including calibration
    def reset(self):
        self.graph.clear()
        self.curve = self.graph.plot(numpy.arange(self.value_history.size), self.value_history, pen = self.green_pen, skipFiniteCheck = True)
        self.capture_index = 0
        self.alarm_off()
        self.rate_alarm_active = False 
        self.calibrating = self.value_history_max + 1
        self.value_history = numpy.zeros(self.value_history_max)
        self.time_history  = numpy.zeros(self.value_history_max)

def check_resolution(app):
    screen = app.primaryScreen().size()
    size_string = str(screen.width()) + " x " + str(screen.height())
    print("Detected resolution: " + size_string)
    if(screen.width() < 1024 or screen.height() < 768):
        error_message = QtWidgets.QMessageBox()
        error_message.setWindowTitle("Notice")
        error_message.setText("The reccomended minimum display resolution is 1024x768.\n\nYour resolution: " + size_string)
        error_message.exec_()   

def print_sys_info():
    print(VERSION)
    print(time.ctime())
    print(platform.platform())
    print("Python Version: " + platform.python_version())
    print('-' * 80)

def main():
    print_sys_info()
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    check_resolution(app)   
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

