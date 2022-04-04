#!/usr/bin/python
from PyQt5 import QtWidgets, uic, QtCore, QtWidgets
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import statistics as stat
import sys, os, math, serial, time, numpy
import serial.tools.list_ports
from scipy import signal
from ecg_viewer_window import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Load the UI Page
        #uic.loadUi('ecg_viewer_window.pyui', self)            
                
        # Capture timer
        self.capture_timer = QtCore.QTimer()
        self.capture_timer.timeout.connect(self.get_input)
        self.capture_rate_ms = 20
        self.capture_timer_qt = QtCore.QElapsedTimer()
        self.capture_timer_qt.start()
        
        # graph timer
        self.graph_timer = QtCore.QTimer()
        self.graph_timer.timeout.connect(self.draw_graph)
        self.graph_frame_rate = 30                                 # change to adjust refresh rate
        self.graph_timer_ms = int(1 / (self.graph_frame_rate / 1000))
        
        # heart rate timer
        self.hr_timer = QtCore.QTimer()
        self.hr_timer.timeout.connect(self.update_hr)
        
        # Connect buttons to methods
        self.button_refresh.clicked.connect(self.com_refresh)
        self.button_connect.clicked.connect(self.com_connect)  
        self.button_reset.clicked.connect(self.reset_graph)
        self.button_run.clicked.connect(self.run_toggle)
        self.button_run.setDisabled(True)
        
        # connection status
        self.ser = None
        self.com_port = ''

        # perform initial com port check
        self.com_refresh()  
        
        # set graph properties
        self.graph.showGrid(True, True, alpha = 0.5)  
        
        # data variables
        self.current_reading = 0
        self.value_history_max = 200
        self.value_history = [0] * self.value_history_max
        self.mean = 0 
        self.invert_modifier = 1
        self.calibrating = self.value_history_max
        self.peaks = list()
        
        # data over time storage
        self.value_history_timed = list()
        self.reset_graph()

        # run state
        self.run = True
    
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
                self.ser = serial.Serial(self.com_port, 115200)
                self.button_refresh.setDisabled(True)
                self.button_connect.setText("Disconnect")
                self.statusBar.showMessage("Connected to " + self.com_port)
                time.sleep(3)
                self.ser.flushInput()
                self.capture_timer.start(self.capture_rate_ms)
                self.hr_timer.start(1000)
                self.graph_timer.start(self.graph_timer_ms)
                self.calibrating = self.value_history_max
                self.invert_modifier = 1
                self.button_run.setDisabled(False)
        # re-add the try and uncomment below later
            except Exception as e:
                error_message = QtWidgets.QMessageBox()
                error_message.setWindowTitle("Connection Error")
                error_message.setText(str(e))
                error_message.exec_()
                print(e)
        else:
            self.button_run.setDisabled(True)
            self.capture_timer.stop()
            self.hr_timer.stop()
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
            buf = buf + str(self.ser.read().decode())
        try:
            buf = buf.strip('\n').strip('\r')
            self.current_reading = float(buf)
            assert(self.invert_modifier == 1 or self.invert_modifier == -1)
            #if(self.current_reading < 20):
            #    self.ser.flush()
            #    return
            val = self.invert_modifier * self.current_reading
            self.value_history.append(val)
            self.value_history_timed.append([val, self.capture_timer_qt.elapsed()])
            self.value_history_timed.pop(0)
            self.value_history.pop(0)
        except Exception as e:
            print(e)
            
        # Perform calibration. Capture data as normal until self.calibrating counter is zero.
        # If the peak value is below the mean, invert the signal.
        if(self.calibrating > 0):
            self.calibrating = self.calibrating - 1
        elif(self.calibrating == 0):
            min_delta = self.mean - min(self.value_history[50:100])
            max_delta = max(self.value_history[50:100]) - self.mean
            if(min_delta > max_delta):
                self.invert_modifier = -1
                self.statusBar.showMessage('Inverting input signal')   
            else:
                self.invert_modifier = 1
            self.calibrating = -1
            
        # update graph
        #self.draw_graph()
        
    # Clear and refresh graph 
    def draw_graph(self):
        red_pen = pg.mkPen('r')
        green_pen = pg.mkPen('g')
        yellow_pen = pg.mkPen('y')
        self.graph.clear()
        self.mean = stat.mean(self.value_history)
        center = (max(self.value_history) - ((max(self.value_history) - min(self.value_history)) / 2))
        self.graph.plot([*range(len(self.value_history))], self.value_history, pen = green_pen)
        
        # Visually shows signal tracking information. SLOW
        if(self.show_track.isChecked()):
            center = self.detect_peaks()
            center_line = pg.InfiniteLine(pos = center, angle = 0, movable = False, pen = yellow_pen)
            self.graph.addItem(center_line)
            mean = pg.InfiniteLine(pos = self.mean, angle = 0, movable = False, pen = red_pen)
            self.graph.addItem(mean)

            # display a vertical line intersecting each detected peak
            for p in self.peaks[::-1][0:2]:
                l = pg.InfiniteLine(pos = p, angle = 90, movable = False)
                self.graph.addItem(l)  
            
            # display holdoff  
            for p in self.peaks[::-1][1:2]:
                l = pg.InfiniteLine(pos = p + 15, angle = 90, movable = False, pen = pg.mkPen(color=(200, 200, 255), style = QtCore.Qt.DotLine))
                self.graph.addItem(l) 
    
    # Update the heart rate LCD reading. 
    # Converts the average time between peaks to frequency 
    # (1 / (<avg peak distance> * <capture rate in ms>)) * 60 * 1000
    def update_hr(self):
        self.detect_peaks()
        times = list()
        if(len(self.peaks) > 1):
            for i, v in enumerate(self.peaks):
                if(i != 0):
                    last = self.value_history_timed[self.peaks[i - 1]][1]
                    times.append(self.value_history_timed[v][1] - last)
        if(len(times)):
            f = (1 / (sum(times) / len(times)))
            self.lcdNumber.display(f * 1000 * 60)
        else:
            self.lcdNumber.display(0)
    
    # clear all history, including calibration
    def reset_graph(self):
        self.value_history = [0] * self.value_history_max
        self.calibrating = self.value_history_max
        self.invert_modifier = 1
        self.value_history_timed = list()
        for i in range(self.value_history_max):
            self.value_history_timed.append([0, -1])
    
    # detect peaks using scipy. 
    #   prominence: the threshold the peak needs to be at, relative to the surrounding samples
    #   distance  : (AKA holdoff) minimum required distance between the previous peak to the next peak
    #   height    : minimum height of peak to be accepted
    # modifies:  stores index of peaks in self.peaks 
    # returns :  center (not average) of recorded values
    def detect_peaks(self, sig_prominence = 20, sig_distance = 13):
        center = (max(self.value_history) - ((max(self.value_history) - min(self.value_history)) / 2))
        self.peaks = signal.find_peaks(
                    self.value_history, 
                    prominence = sig_prominence,
                    height = center,
                    distance = sig_distance,
                )[0]
        return center
    
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
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

