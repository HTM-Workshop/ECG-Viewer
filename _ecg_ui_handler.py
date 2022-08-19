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

import csv
import time
import pyqtgraph.exporters
from PyQt5 import QtWidgets, QtCore


def ui_set_tooltips(self):
    """Sets the UI tooltips."""
    self.holdoff_box.setToolTip("Time to wait until it detects the next peak. Set higher if the heart rate triggers too quickly.")
    self.prominence_box.setToolTip("The expected magnitude of the peaks. Lower to increase sensitivity.")
    self.button_ui_force_invert.setToolTip("Inverts the waveform. Useful if calibration didn't automatically invert the signal.")
    self.show_track.setToolTip("Show the real-time peak detection. Disables filtering while on")
    self.button_reset.setToolTip("Clears graph data. Forces recalibration.")
    self.button_run.setToolTip("Pauses data capture.")
    self.button_refresh.setToolTip("Refresh the list of connected devices.")
    self.button_connect.setToolTip("Connected to the selected device.")
    self.graph_zoom_slider.setToolTip("Changes the vertical zoom of the graph.")
    self.window_length_box.setToolTip("Higher values give more consistent filtering, but increases bias error. VALUE MUST BE ODD.")
    self.polyorder_box.setToolTip("Determines the 'complexity' of the filtering applied. Higher values retain more resolution.")
    self.actionBold_Line.setToolTip("Draws graph with thicker line. Reduces visual accuracy. Slower.")


def ui_holdoff_box_update(self):
    """
    Enables/disables the holdoff box depending on if the Auto Holdoff menu option
    is checked or not
    """

    if self.actionAuto_Holdoff.isChecked():
        self.holdoff_box.setDisabled(True)
    else:
        self.holdoff_box.setDisabled(False)

# message box methods
def ui_alarm_on(self, text):
    """Display alarm text in alert box."""
    self.alarm_text.setText("")
    self.alarm_window.setStyleSheet("QFrame { background-color: red }")
    self.alarm_text.setText(text)

    
def ui_alarm_off(self):
    """Clear alert box."""
    self.alarm_text.setText("")
    self.alarm_window.setStyleSheet("QFrame { background-color: white }")


def ui_set_message(self, text):
    """Display status message in alert box."""
    self.alarm_text.setText("")
    self.alarm_window.setStyleSheet("QFrame { background-color: white }")
    self.alarm_text.setText(text)

    
def ui_clear_message(self):
    """Clear alert box."""
    self.alarm_window.setStyleSheet("QFrame { background-color: white }")
    self.alarm_text.setText("")


def ui_force_invert(self):
    """Forces inversion of the graph data. Should be called from UI button."""
    self.invert_modifier = self.invert_modifier * -1


def ui_display_error_message(self, title: str, msg: str) -> None:
    """Display a generic error message to the user."""
    error_message = QtWidgets.QMessageBox()
    error_message.setWindowTitle(title)
    error_message.setText(msg)
    error_message.exec_()


def ui_statusbar_message(self, msg) -> None:
    """
    Display a message in the status bar.
    """
    
    self.statusBar.showMessage(str(msg))


# toggle capture on or off
def ui_run_toggle(self):
    """Toggles the capture process on or off. Should be called by a single run/stop function."""
    assert self.ser.isOpen()
    if(self.capture_timer.isActive()):
        self.statusBar.showMessage('Capture stopped')
        self.button_run.setText("Run")
        self.ser_stop_capture_timer()
    else:
        self.statusBar.showMessage('Capture running')
        self.button_run.setText("Stop")
        self.ser_start_capture_timer()


def ui_show_about(self):
    """Shows the About dialog window."""
    self.about_window.show()


def ui_export_data_raw(self):
    """
    Exports a RAW binary data file of the currently recorded information, pre-filtered.\n
    Pauses capture (if running) and shows a file save dialog.\n
    Resumes capture if itw as running after file is saved or user cancels save..
    """

    capture_running = self.capture_timer.isActive()
    self.ser_stop_capture_timer()
    default_filename = str(time.time()).split('.', maxsplit=1)[0] + '.bin'
    filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", directory = default_filename)[0]
    if filename:
        try:
            f = open(filename, 'wb')
            data = [int(abs(x)).to_bytes(2, 'little') for x in self.value_history]
            data = b''.join(data)
            f.write(data)
            f.flush()
            f.close()
        except Exception as e:
            self.ui_display_error_message("Export Error", e)
    if(capture_running):
        self.ser_start_capture_timer()


def ui_export_data_png(self):
    """
    Exports a PNG image file of the currently displayed information.\n
    Pauses capture (if running) and shows a file save dialog.\n
    Resumes capture if itw as running after file is saved or user cancels save..
    """

    capture_running = self.capture_timer.isActive()
    self.ser_stop_capture_timer()
    default_filename = str(time.time()).split('.', maxsplit=1)[0] + '.png'
    filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", directory = default_filename)[0]
    if filename:
        try:
            QtCore.QCoreApplication.processEvents()
            exporter = pyqtgraph.exporters.ImageExporter(self.graph.getPlotItem())
            exporter.export(filename)
        except Exception as e:
            self.ui_display_error_message("Export Error", e)
    if(capture_running):
        self.ser_start_capture_timer()


def ui_export_data_csv(self):
    """
    Exports a CSV file of the currently recorded information, pre-filtered.\n
    Pauses capture (if running) and shows a file save dialog.\n
    Resumes capture if itw as running after file is saved or user cancels save..
    """

    capture_running = self.capture_timer.isActive()
    self.ser_stop_capture_timer()
    default_filename = str(time.time()).split('.', maxsplit=1)[0] + '.csv'
    filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", directory = default_filename)[0]
    if filename:
        try:
            csv_file = open(filename, 'w', newline = '')
            writer = csv.writer(csv_file)
            writer.writerow(self.value_history)
            csv_file.flush()
            csv_file.close()
        except Exception as e:
            self.ui_display_error_message("Export Error", e)
    if(capture_running):
        self.ser_start_capture_timer()