#!/usr/bin/python
from PyQt5 import QtWidgets, uic, QtCore, QtWidgets
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import statistics as stat
import sys, os, math, serial, time, numpy
import serial.tools.list_ports
from scipy import signal

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.current_reading = 0
        self.value_history_max = 200
        self.value_history = [0] * self.value_history_max

        # Load the UI Page
        uic.loadUi('ecg_viewer_window.ui', self)            
                
        # Capture timer
        self.capture_timer = QtCore.QTimer()
        self.capture_timer.timeout.connect(self.get_input)
        self.capture_rate_ms = 20
        
        # heart rate timer
        self.hr_timer = QtCore.QTimer()
        self.hr_timer.timeout.connect(self.update_hr)

        
        # Connect buttons to methods
        self.button_refresh.clicked.connect(self.com_refresh)
        self.button_connect.clicked.connect(self.com_connect)  
        self.button_reset.clicked.connect(self.reset_graph)
        
        # connection status
        self.ser = None
        self.com_port = ''

        # perform initial com port check
        self.com_refresh()  
        
        self.graph.showGrid(True, True, alpha = 0.5)  
        
    def com_refresh(self):
        self.port_combo_box.clear()
        self.available_ports = serial.tools.list_ports.comports()
        for i in self.available_ports:
            self.port_combo_box.addItem(i.device)  
        com_count = self.port_combo_box.count()    
           
    def com_connect(self):
        if(self.ser == None):
            try:
                self.com_port = self.port_combo_box.currentText()
                if(self.com_port == ''):
                    self.statusBar.showMessage('No device selected!')
                    return
                self.ser = serial.Serial(self.com_port, 115200)
                self.button_refresh.setDisabled(True)
                self.button_connect.setText("Disconnect")
                self.statusBar.showMessage("Connected to " + self.com_port)
                time.sleep(3)
                self.ser.flushInput()
                self.capture_timer.start(self.capture_rate_ms)
                self.hr_timer.start(1000)
        # re-add the try and uncomment below later
            except Exception as e:
                error_message = QtWidgets.QMessageBox()
                error_message.setWindowTitle("Connection Error")
                error_message.setText(str(e))
                error_message.exec_()
                print(e)
        else:
            self.capture_timer.stop()
            self.hr_timer.stop()
            self.ser.close()
            self.ser = None
            self.button_refresh.setDisabled(False)
            self.button_connect.setText("Connect")
            self.statusBar.showMessage('No device connected')   
                
    # Send a value to the Arduino to trigger it to do a measurement
    def get_input(self):
        try:
            self.ser.write('\n'.encode())
        except Exception as e:
            self.ser == None
            self.com_connect()
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText(str(e))
            msg.setWindowTitle("Notice")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
        buf = ''
        while(self.ser.inWaiting() > 0):
            buf = buf + str(self.ser.read().decode())
        try:
            buf = buf.strip('\n').strip('\r')
            self.current_reading = float(buf)
            self.value_history.append(self.current_reading)
            if(len(self.value_history) > self.value_history_max):
                self.value_history.pop(0)
        except:
            pass
        self.draw_graph()
    def draw_graph(self):
        #b, a = signal.butter(2, 1, 'hp', fs = 30)
        #filtered = signal.filtfilt(b, a, self.value_history)
        red_pen = pg.mkPen('r')
        green_pen = pg.mkPen('g')
        yellow_pen = pg.mkPen('y')
        self.graph.clear()
        #self.graph.plot([*range(len(filtered) - 25)], filtered[0:175], pen = red_pen)
        center = (max(self.value_history) - ((max(self.value_history) - min(self.value_history)) / 2))
        self.graph.plot([*range(len(self.value_history))], self.value_history, pen = red_pen)
        if(self.show_track.isChecked()):
            center_line = pg.InfiniteLine(pos = center, angle = 0, movable = False, pen = yellow_pen)
            self.graph.addItem(center_line)
            mean = pg.InfiniteLine(pos = stat.mean(self.value_history), angle = 0, movable = False, pen = green_pen)
            self.graph.addItem(mean)
            peaks = signal.find_peaks(
                        self.value_history, 
                        prominence = 20,
                        height = center,
                        distance = 30,
                    )[0]
            for p in peaks:
                l = pg.InfiniteLine(pos = p, angle = 90, movable = False, pen = pg.mkPen('c'))
                self.graph.addItem(l)            
    def update_hr(self):
        center = (max(self.value_history) - ((max(self.value_history) - min(self.value_history)) / 2))
        peaks = signal.find_peaks(
                    self.value_history, 
                    prominence = 20,
                    height = center,
                    distance = 30,
                )[0]
        times = list()
        if(len(peaks) > 1):
            for i, v in enumerate(peaks):
                if(i < len(peaks) - 1):
                    times.append(peaks[i + 1] - peaks[i])
        if(len(times)):
            f = (1 / (sum(times) / len(times) * self.capture_rate_ms))
            self.lcdNumber.display(int(f * 60 * 1000))
        else:
            self.lcdNumber.display(0)
            
    def reset_graph(self):
        self.value_history = [0] * self.value_history_max
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

