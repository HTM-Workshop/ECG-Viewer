import serial.tools.list_ports
import serial, time
from PyQt5 import QtWidgets, uic, QtCore
import statistics as stat
from ecg_viewer_window import Ui_MainWindow
# refresh available devices, store in dropdown menu storage    
def com_refresh(self):
    self.port_combo_box.clear()
    self.available_ports = serial.tools.list_ports.comports()
    for i in self.available_ports:
        self.port_combo_box.addItem(i.device)  
    com_count = self.port_combo_box.count()    

# connect to device
def com_connect(self):
    self.run = True
    self.button_run.setText("Stop")
    if(self.ser == None):
        try:
            self.statusBar.showMessage("Connecting...")
            self.com_port = self.port_combo_box.currentText()
            if(self.com_port == ''):
                self.statusBar.showMessage('No device selected!')
                return
            self.reset()
            self.ser = serial.Serial(self.com_port, 115200)
            self.button_refresh.setDisabled(True)
            self.button_connect.setText("Disconnect")
            self.statusBar.showMessage("Connected to " + self.com_port)
            time.sleep(3)
            self.ser.flushInput()
            self.capture_timer.start(self.capture_rate_ms)
            self.graph_timer.start(self.graph_timer_ms)
            self.invert_modifier = 1
            self.button_run.setDisabled(False)
            self.set_message("CALIBRATING")
        except Exception as e:
            error_message = QtWidgets.QMessageBox()
            error_message.setWindowTitle("Connection Error")
            error_message.setText(str(e))
            error_message.exec_()
            print(e)
    else:
        self.button_run.setDisabled(True)
        self.capture_timer.stop()
        self.graph_timer.stop()
        self.ser.close()
        self.ser = None
        self.button_refresh.setDisabled(False)
        self.button_connect.setText("Connect")
        self.statusBar.showMessage('No device connected')   
        
# Send a value to the Arduino to trigger it to do a measurement
def get_input(self):
    try:
        self.ser.write('\n'.encode())
        self.ser.flush()
    except Exception as e:
        self.ser == None
        self.com_connect()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Connection to Arduino lost. \nPlease check cable and click connect.\n\nError information:\n" + str(e))
        msg.setWindowTitle("Connection Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
    buf = ''
    while(self.ser.inWaiting() > 0):
        c = str(self.ser.read().decode())
        buf = buf + c
        if c == '\n':
            break
    try:
        buf = buf.strip('\n')
        buf = buf.replace('\r', '')
        buf = buf.split('\n')[0]
        self.current_reading = float(buf)
        assert(self.invert_modifier == 1 or self.invert_modifier == -1)
        val = self.invert_modifier * self.current_reading
        self.value_history[self.capture_index] = val
        self.value_history_timed[self.capture_index] = [val, self.capture_timer_qt.elapsed()]
        self.capture_index = (self.capture_index + 1) % self.value_history_max 
    except Exception as e:
        pass
        
    # Perform calibration. Capture data as normal until self.calibrating counter is zero.
    # If the peak value is below the mean, invert the signal.
    if(self.calibrating > 0):
        self.calibrating = self.calibrating - 1
    elif(self.calibrating == 0):
        self.clear_message()
        period_mean = stat.mean(self.value_history[50:100])
        min_delta = period_mean - min(self.value_history[50:100])
        max_delta = max(self.value_history[50:100]) - period_mean
        print("DYNAMIC CALIBRATION INFO:")
        print("MAX      : " + str(max(self.value_history[50:100])))
        print("MIN      : " + str(min(self.value_history[50:100])))
        print("MEAN     : " + str(period_mean))
        print("MAX DELTA: " + str(max_delta))
        print("MIN DELTA: " + str(min_delta))
        print("CIDX     : " + str(self.capture_index))
        if(self.autoinvert_checkbox.isChecked()):
            if(min_delta > max_delta):
                self.invert_modifier = -1
                self.statusBar.showMessage('Inverting input signal')   
            else:
                self.invert_modifier = 1
        self.calibrating = -1
        if(max_delta == 0 and min_delta == 0):
            error_message = QtWidgets.QMessageBox()
            error_message.setWindowTitle("Device Error")
            error_message.setText("Connected device is not responding.\n\nThis may be the incorrect device. Please choose\na different device in the menu and try again.")
            error_message.exec_()
            self.reset()
            self.com_connect()
