from PyQt5 import QtWidgets, uic, QtCore
import time

# message box methods
def alarm_on(self, text):
    self.alarm_window.setStyleSheet("QFrame { background-color: red }")
    self.alarm_text.setText(text)
def alarm_off(self):
    self.alarm_window.setStyleSheet("QFrame { background-color: white }")
    self.alarm_text.setText("")
def set_message(self, text):
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

# exports data stored in self.value_history to a binary file 
def export_data(self):
    try:
        filename = str(time.time()).split('.')[0] + '.bin'
        f = open(filename, 'wb')
        data = [int(abs(x)).to_bytes(2, 'little') for x in self.value_history]
        data = b''.join(data) 
        f.write(data)
        f.flush()
        f.close()
        message = QtWidgets.QMessageBox()
        message.setWindowTitle("Export Success")
        message.setText("Raw binary record has been exported to the local directory")
        message.exec_()
    except Exception as e:
        error_message = QtWidgets.QMessageBox()
        error_message.setWindowTitle("Export Error")
        error_message.setText(str(e))
        error_message.exec_()
        print(e)
