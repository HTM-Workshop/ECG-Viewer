from distutils.log import debug
from typing import Type
import serial.tools.list_ports
import serial, time, numpy
from PyQt5 import QtWidgets, uic, QtCore
import statistics as stat
from debug import debug_timer
from ecg_viewer_window import Ui_MainWindow

# refresh available devices, store in dropdown menu storage    
@debug_timer
def com_refresh(self):
    self.port_combo_box.clear()
    available_ports = serial.tools.list_ports.comports()
    for device in available_ports:
        d_name = device.device + ": " + device.description
        self.port_combo_box.addItem(d_name, device.device)

# checks to see if we can communicate with the Arduino
# returns True if device is responding, False if not.
@debug_timer
def com_check_device(self):
    self.statusBar.showMessage('Connecting...')
    max_attempts = 10
    device_ok = False
    while(max_attempts > 0 and device_ok == False):
        try:
            self.ser.write('\n'.encode())
            self.ser.flush()
            while(self.ser.inWaiting() > 0):
                c = str(self.ser.read().decode())
                if c == '$':
                    device_ok = True
                    break    
        except Exception as e:
            print(e)
            time.sleep(1)
        max_attempts -= 1
        time.sleep(0.2)
    return device_ok

@debug_timer
def com_connect(self):
    """Connect/Disconnect from a serial device."""
    # fetch port name from dropdown menu
    try:
        current_index = self.port_combo_box.currentIndex()
        com_port = self.port_combo_box.itemData(current_index) 
        if not com_port:
            raise ValueError("No port selected.")
    except ValueError:
        self.statusBar.showMessage('No device selected!')
        return False
    except TypeError as e:
        self.display_error_message("Invalid port type", e)
        print(e)
        return False
    
    # connect to port 
    try:
        self.ser.port = com_port
        self.ser.open()
    except serial.Serial.SerialException as e:
        self.display_error_message("Connection Failure", e)
        return False

    # detect if device is responding properly
    if not self.com_check_device():
        self.display_error_message("Device Error", """Connected device is not responding.\n\nThis may be the incorrect device. Please choose a different device in the menu and try again.""")
        self.ser.close()
        return False
    
    # device is connected and test has passed
    return True

# connect to device
# def com_connect(self):
#     self.run = True
#     self.button_run.setText("Stop")
#     if(self.ser == None):
#         try:
#             #self.com_port = self.port_combo_box.currentText().split(':')[0]
#             current_index = self.port_combo_box.currentIndex()
#             com_port = self.port_combo_box.itemData(current_index)            
#             if(com_port == ''):
#                 self.statusBar.showMessage('No device selected!')
#                 return
#             self.reset()
#             self.ser = serial.Serial(com_port, 115200)
#             self.ser.flushInput()
#             device_ok = self.com_check_device()
#             if(not device_ok):
#                 self.connection_error_msg()
#                 self.ser = None
#                 return    
#         except Exception as e:
#             error_message = QtWidgets.QMessageBox()
#             error_message.setWindowTitle("Connection Error")
#             error_message.setText(str(e))
#             error_message.exec_()
#             print(e)
#         self.button_refresh.setDisabled(True)
#         self.button_connect.setText("Disconnect")
#         self.statusBar.showMessage("Connected to " + com_port)
#         self.capture_timer.start(self.capture_rate_ms)
#         self.graph_timer.start(self.graph_timer_ms)
#         self.invert_modifier = 1
#         self.button_run.setDisabled(False)
#         self.set_message("CALIBRATING")
#     else:
#         self.button_run.setDisabled(True)
#         self.capture_timer.stop()
#         self.graph_timer.stop()
#         self.ser.close()
#         self.ser = None
#         self.button_refresh.setDisabled(False)
#         self.button_connect.setText("Connect")
#         self.statusBar.showMessage('No device connected')   
        
# Fetch a value from the Arduino
def get_input(self):

    # send character to Arduino to trigger the Arduino to begin a analogRead capture
    try:
        self.ser.write('\n'.encode())
        #self.ser.flush()
    except Exception as e:
        self.ser == None
        self.com_connect()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Connection to Arduino lost. \nPlease check cable and click connect.\n\nError information:\n" + str(e))
        msg.setWindowTitle("Connection Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()

    # get response from Arduino, terminated by newline character
    buf = ''
    while(self.ser.inWaiting() > 0):
        c = str(self.ser.read().decode())
        if c == '$':
            break
    while(self.ser.inWaiting() > 0):
        c = str(self.ser.read().decode())
        buf = buf + c
        if c == '\n':
            break

    # parse the input from the Arduino.
#        buf = buf[buf.find('$'):]
#        buf = buf.replace('\r', '')
#        buf = buf[1:buf.find('\n')].strip('\n')     # start slice at 1 to drop '$' character
    buf = buf.strip('\n')
    if len(buf) != 3:
        return
    self.current_reading = int(buf)
    val = self.invert_modifier * self.current_reading
    self.value_history[self.capture_index] = val
    self.time_history[self.capture_index] = self.capture_timer_qt.elapsed()
    self.capture_index = (self.capture_index + 1) % self.value_history_max 
    
    # Perform calibration. Capture data as normal until self.calibrating counter is zero.
    # If the peak value is below the mean, invert the signal.
    if(self.calibrating > 0):
        self.calibrating = self.calibrating - 1
    elif(self.calibrating == 0):
        self.clear_message()
        window = 150
        peak_samples = 3
        temp_array = self.value_history[window:self.value_history_max - window].copy()
        temp_array.sort()
        period_mean = self.value_history[window:self.value_history_max - window].mean()
        min_delta = period_mean - stat.mean(temp_array[0:peak_samples])
        print(temp_array[0:peak_samples])
        temp_array = temp_array[::-1]
        max_delta = stat.mean(temp_array[0:peak_samples]) - period_mean
        print(temp_array[0:peak_samples])
        
        #min_delta = period_mean - min(self.value_history[50:self.value_history_max - 50])
        #max_delta = max(self.value_history[50:self.value_history_max - 50]) - period_mean
        print("DYNAMIC CALIBRATION INFO:")
        print("RANGE     : " + str(window) + " - " + str(self.value_history_max - window))
        print("PK SAMPLES: " + str(peak_samples))
        print("AVG MAX   : " + str(self.value_history[window:self.value_history_max - window].max()))
        print("AVG MIN   : " + str(self.value_history[window:self.value_history_max - window].min()))
        print("MEAN      : " + str(period_mean))
        print("MAX DELTA : " + str(max_delta))
        print("MIN DELTA : " + str(min_delta))
        print("CIDX      : " + str(self.capture_index))
        if(abs(max_delta - min_delta) > 1.5):
            if(self.autoinvert_checkbox.isChecked()):
                if(min_delta > max_delta):
                    self.invert_modifier = self.invert_modifier * -1
                    self.statusBar.showMessage('Inverting input signal')  
                    print("*** INVERTING SIGNAL ***") 
        else:
            print("*** NO SIGNAL DETECTED ***")
        self.calibrating = -1
        if(max_delta == 0 and min_delta == 0):
            self.connection_error_msg()
            self.reset()
            self.com_connect()

def stop_capture_timer(self):
    if(self.capture_timer.isActive()):
        self.stop_graph_timer()
        self.capture_timer.stop()

def start_capture_timer(self):
    self.ser.reset_input_buffer()
    if(not self.capture_timer.isActive()):
        self.capture_timer.start(self.capture_rate_ms)
        self.start_graph_timer()

def restart_capture_timer(self):
    self.ser.reset_input_buffer()
    self.capture_rate_ms = self.CaptureRateGroup.checkedAction().data()
    if(self.capture_timer.isActive()):
        self.capture_timer.stop()
        self.capture_timer.start(self.capture_rate_ms)

