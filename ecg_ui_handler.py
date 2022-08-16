import csv
import time
import pyqtgraph.exporters
from PyQt5 import QtWidgets, uic, QtCore


# message box methods
def alarm_on(self, text):
    self.alarm_text.setText("")
    self.alarm_window.setStyleSheet("QFrame { background-color: red }")
    self.alarm_text.setText(text)
def alarm_off(self):
    self.alarm_text.setText("")
    self.alarm_window.setStyleSheet("QFrame { background-color: white }")
def set_message(self, text):
    self.alarm_text.setText("")
    self.alarm_window.setStyleSheet("QFrame { background-color: white }")
    self.alarm_text.setText(text)
def clear_message(self):
    self.alarm_window.setStyleSheet("QFrame { background-color: white }")
    self.alarm_text.setText("")
def force_invert(self):
    self.invert_modifier = self.invert_modifier * -1
    
def display_error_message(self, title: str, msg: str) -> None:
    """Display a generic error message to the user."""
    error_message = QtWidgets.QMessageBox()
    error_message.setWindowTitle(title)
    error_message.setText(msg)
    error_message.exec_()  
    

# toggle capture on or off
def run_toggle(self):
    assert self.ser.isOpen()
    if(self.capture_timer.isActive()):
        self.statusBar.showMessage('Capture stopped')  
        self.button_run.setText("Run")
        self.stop_capture_timer()
    else:
        self.statusBar.showMessage('Capture running') 
        self.button_run.setText("Stop")
        self.start_capture_timer()

def show_about(self):
    self.about_window.show()

# ISSUE: These export options fail on MacOS when compiled to a .apps 
# exports data stored in self.value_history to a binary file 
def export_data_raw(self):
    capture_running = self.capture_timer.isActive()
    self.stop_capture_timer()
    default_filename = str(time.time()).split('.')[0] + '.bin'
    filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", directory = default_filename)[0]
    if(filename != ""):
        try:
            f = open(filename, 'wb')
            data = [int(abs(x)).to_bytes(2, 'little') for x in self.value_history]
            data = b''.join(data) 
            f.write(data)
            f.flush()
            f.close()
        except Exception as e:
            error_message = QtWidgets.QMessageBox()
            error_message.setWindowTitle("Export Error")
            error_message.setText(str(e))
            error_message.exec_()
            print(e)
    if(capture_running):
        self.start_capture_timer()

def export_data_png(self):
    capture_running = self.capture_timer.isActive()
    self.stop_capture_timer()
    default_filename = str(time.time()).split('.')[0] + '.png'
    filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", directory = default_filename)[0]
    if(filename != ""):
        try:
            QtCore.QCoreApplication.processEvents()
            exporter = pyqtgraph.exporters.ImageExporter(self.graph.getPlotItem())
            exporter.export(filename)
        except Exception as e:
            error_message = QtWidgets.QMessageBox()
            error_message.setWindowTitle("Export Error")
            error_message.setText(str(e))
            error_message.exec_()
            print(e)
    if(capture_running):
        self.start_capture_timer()

def export_data_csv(self):
    capture_running = self.capture_timer.isActive()
    self.stop_capture_timer()
    default_filename = str(time.time()).split('.')[0] + '.csv'
    filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", directory = default_filename)[0]
    if(filename != ""):
        try:
            csv_file = open(filename, 'w', newline = '')
            writer = csv.writer(csv_file)
            writer.writerow(self.value_history)
            csv_file.flush()
            csv_file.close()      
        except Exception as e:
            error_message = QtWidgets.QMessageBox()
            error_message.setWindowTitle("Export Error")
            error_message.setText(str(e))
            error_message.exec_()
            print(e)
    if(capture_running):
        self.start_capture_timer()