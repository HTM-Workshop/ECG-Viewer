from email.policy import default
from PyQt5 import QtWidgets, uic, QtCore
import pyqtgraph.exporters
import time, csv

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
    
    
# toggle capture on or off
def run_toggle(self):
    if(self.ser != None):
        if(self.run == True):
            self.run = False
            self.statusBar.showMessage('Capture stopped')  
            self.button_run.setText("Run")
            self.capture_timer.stop()
        else:
            self.run = True
            self.statusBar.showMessage('Capture running') 
            self.button_run.setText("Stop")
            self.capture_timer.start(self.capture_rate_ms)

def show_about(self):
    self.about_window.show()

# ISSUE: These export options fail on MacOS when compiled to a .apps 
# exports data stored in self.value_history to a binary file 
def export_data_raw(self):
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
    self.start_capture_timer()

def export_data_png(self):
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
    self.start_capture_timer()

def export_data_csv(self):
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
    self.start_capture_timer()