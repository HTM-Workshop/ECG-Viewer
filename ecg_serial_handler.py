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
        self.display_error_message("Invalid port type", str(e))
        print(e)
        return False
    
    # connect to port 
    try:
        self.ser.port = com_port
        self.ser.open()
    except serial.serialutil.SerialException as e:
        self.display_error_message("Connection Failure", str(e))
        return False

    # detect if device is responding properly
    if not self.com_check_device():
        self.display_error_message("Device Error", """Connected device is not responding.\n\nThis may be the incorrect device. Please choose a different device in the menu and try again.""")
        self.ser.close()
        return False
    
    # device is connected and test has passed
    print("Connection to {} succesful.".format(com_port))
    return True  
        
# Fetch a value from the Arduino
def get_input(self) -> None:
    """Fetches a measurement from the Arduino, stores value in value_history and time_history"""

    # send character to Arduino to trigger the Arduino to begin a analogRead capture
    try:
        self.ser.write('\n'.encode())
    except Exception as e:
        self.ser == None
        self.connect_toggle()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Connection to Arduino lost. \nPlease check cable and click connect.\n\nError information:\n" + str(e))
        msg.setWindowTitle("Connection Error")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
        return

    # get response from Arduino, terminated by newline character
    buf = ''

    # read and discard incoming bytes until the start character is found
    while(self.ser.inWaiting() > 0):
        c = str(self.ser.read().decode())
        if c == '$':
            break

    # read characters until newline is detected, this is faster than serial's read_until
    while(self.ser.inWaiting() > 0):
        c = str(self.ser.read().decode())
        if c == '\n':
            break
        buf = buf + c

    # all measurements are exactly three characters in size
    if len(buf) != 3:
        return False
    self.current_reading = int(buf)
    val = self.invert_modifier * self.current_reading
    self.value_history[self.capture_index] = val
    self.time_history[self.capture_index] = self.capture_timer_qt.elapsed()
    self.capture_index = (self.capture_index + 1) % self.value_history_max 
    return True

def do_calibrate(self):    
    """ Perform calibration. Capture data as normal until self.calibrating counter is zero.
     If the peak value is below the mean, invert the signal. """
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
        temp_array = temp_array[::-1]
        max_delta = stat.mean(temp_array[0:peak_samples]) - period_mean
        if(abs(max_delta - min_delta) > 1.5):
            if(self.autoinvert_checkbox.isChecked()):
                if(min_delta > max_delta):
                    self.invert_modifier = self.invert_modifier * -1
                    self.statusBar.showMessage('Inverting input signal')  
                    print("*** INVERTING SIGNAL ***") 
        else:
            print("*** NO SIGNAL DETECTED ***")
        self.calibrating = -1
        print("DYNAMIC CALIBRATION INFO:")
        print("RANGE     : {} - {}".format(window, (window, self.value_history_max - window)))
        print("PK SAMPLES: {}".format(peak_samples))
        print("MEAN      : {}".format(period_mean))
        print("MAX DELTA : {}".format(max_delta))
        print("MIN DELTA : {}".format(min_delta))
        print("CIDX      : {}".format(self.capture_index))

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

