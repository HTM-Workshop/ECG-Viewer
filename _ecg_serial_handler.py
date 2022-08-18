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

import time
import serial
import serial.tools.list_ports
import statistics as stat
from debug import debug_timer


# refresh available devices, store in dropdown menu storage
def ser_com_refresh(self):
    """
    Refreshes the list of available serial devices.\n
    Results are stored in the dropdown menu.\n
    Uses addItem to store the device string."""
    self.port_combo_box.clear()
    available_ports = serial.tools.list_ports.comports()
    for device in available_ports:
        d_name = device.device + ": " + device.description
        self.port_combo_box.addItem(d_name, device.device)


@debug_timer
def ser_check_device(self) -> bool:
    """
    Checks to see if the Arduino is responding the way we expect.\n
    Returns True if device is responding properly.\n
    Returns False if device is not responding or is giving improper responses.
    """

    self.ui_statusbar_message('Connecting...')
    max_attempts = 10
    device_ok = False
    while max_attempts > 0 and not device_ok:
        try:
            self.ser.write('\n'.encode())
            self.ser.flush()
            while self.ser.inWaiting() > 0:
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
def ser_com_connect(self) -> bool:
    """
    Connect/Disconnect from the serial device selected in the devices dropdown menu.\n
    Returns True if the connection was sucessful.\n
    False if the connection was unsucessful.
    """

    # fetch port name from dropdown menu
    try:
        current_index = self.port_combo_box.currentIndex()
        com_port = self.port_combo_box.itemData(current_index)
        if not com_port:
            raise ValueError("No port selected.")
    except ValueError:
        self.ui_statusbar_message('No device selected!')
        return False
    except TypeError as e:
        self.ui_display_error_message("Invalid port type", str(e))
        print(e)
        return False

    # connect to port
    try:
        self.ser.port = com_port
        self.ser.open()
    except serial.serialutil.SerialException as e:
        self.ui_display_error_message("Connection Failure", str(e))
        return False

    # detect if device is responding properly
    if not self.ser_check_device():
        self.ui_display_error_message("Device Error", """Connected device is not responding.\n\nThis may be the incorrect device. Please choose a different device in the menu and try again.""")
        self.ser.close()
        return False

    # device is connected and test has passed
    print("Connection to {} succesful.".format(com_port))
    return True


# Fetch a value from the Arduino
def ser_get_input(self) -> bool:
    """Fetches a measurement from the Arduino, stores value in value_history and time_history.\n
    Returns True if reading was valid.
    Returns False if reading was invalid or unsucessful.
    """

    # send character to Arduino to trigger the Arduino to begin a analogRead capture
    try:
        self.ser.write('\n'.encode())
    except Exception as e:
        self.ser_stop_capture_timer()
        print(e)
        print(self.ser.isOpen())
        self.connect_toggle()
        err_msg = "Connection to Arduino lost. \nPlease check cable and click connect.\n\nError information:\n{}".format(e)
        self.ui_display_error_message("Connection Error", err_msg)
        return False

    # get response from Arduino, terminated by newline character
    buf = ''

    # read and discard incoming bytes until the start character is found
    while self.ser.inWaiting() > 0:
        chr = str(self.ser.read().decode())
        if chr == '$':
            break

    # read characters until newline is detected, this is faster than serial's read_until
    while self.ser.inWaiting() > 0:
        chr = str(self.ser.read().decode())
        if chr == '\n':
            break
        buf = buf + chr

    # all measurements are exactly three characters in size
    if len(buf) != 3:
        return False
    self.current_reading = int(buf)
    val = self.invert_modifier * self.current_reading
    self.value_history[self.capture_index] = val
    self.time_history[self.capture_index] = self.capture_timer_qt.elapsed()
    self.capture_index = (self.capture_index + 1) % self.value_history_max
    return True

def ser_do_calibrate(self) -> None:
    """
    Perform calibration. Capture data as normal until self.calibrating counter is zero.\n
    If the peak value is below the mean, invert the signal.
    """

    if self.calibrating > 0:
        self.calibrating = self.calibrating - 1
    elif self.calibrating == 0:
        self.ui_clear_message()
        window = 150
        peak_samples = 3
        temp_array = self.value_history[window:self.value_history_max - window].copy()
        temp_array.sort()
        period_mean = self.value_history[window:self.value_history_max - window].mean()
        min_delta = period_mean - stat.mean(temp_array[0:peak_samples])
        temp_array = temp_array[::-1]
        max_delta = stat.mean(temp_array[0:peak_samples]) - period_mean
        if abs(max_delta - min_delta) > 1.5:
            if self.autoinvert_checkbox.isChecked():
                if min_delta > max_delta:
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

def ser_stop_capture_timer(self):
    """Stops the capture timer AND graph update timer."""
    if self.capture_timer.isActive():
        self.graph_stop_timer()
        self.capture_timer.stop()

def ser_start_capture_timer(self):
    """Starts the capture timer AND graph update timer."""
    self.ser.reset_input_buffer()
    if not self.capture_timer.isActive():
        self.capture_timer.start(self.capture_rate_ms)
        self.graph_start_timer()


