import pyqtgraph as pg
from PyQt5 import QtWidgets, uic, QtCore, QtWidgets
import statistics as stat
from scipy.signal import savgol_filter
from ecg_viewer_window import Ui_MainWindow
import math


# Clear and refresh graph. pyqtgraph works a lot like a frame buffer, so 
# the graph must be cleared before it's redrawn.
def draw_graph(self):
    red_pen = pg.mkPen('r')
    green_pen = pg.mkPen('g')
    yellow_pen = pg.mkPen('y')
    self.graph.clear()                                  # does the actual graph clearing
    self.mean = stat.mean(self.value_history)
    center = (max(self.value_history) - ((max(self.value_history) - min(self.value_history)) / 2))
    try:
        if(self.show_track.isChecked() == False):       # run savgol filter before plotting 
            fdat = savgol_filter(
                self.value_history, 
                window_length = self.window_length_box.value(), 
                polyorder = self.polyorder_box.value(),
                mode = 'interp',
                )[25:self.value_history_max - 25]
            self.graph.plot([*range(len(fdat))], fdat, pen = green_pen, skipFiniteCheck = True)
        else:                                           # otherwise plot raw, unfiltered values
            self.graph.plot([*range(len(self.value_history))], self.value_history, pen = green_pen, skipFiniteCheck = True)
    except Exception as e:
        self.window_length_box.setValue(99)
        self.polyorder_box.setValue(5)
        print(e)

    # Visually shows signal tracking information. VERY SLOW IF ENABLED
    if(self.show_track.isChecked()):
        center = self.detect_peaks()
        center_line = pg.InfiniteLine(pos = center, angle = 0, movable = False, pen = yellow_pen)
        self.graph.addItem(center_line)
        mean = pg.InfiniteLine(pos = self.mean, angle = 0, movable = False, pen = red_pen)
        self.graph.addItem(mean)

        # select datapoints to graph depending on if the capture is activelly running or not
        if(self.run == True):
            sel_peaks = self.peaks[::-1][0:2]
            sel_hold  = self.peaks[::-1][1:2]
        else:
            sel_peaks = self.peaks[::-1]
            sel_hold  = self.peaks[::-1]

        # display a vertical line intersecting each detected peak
        for p in sel_peaks:
            l = pg.InfiniteLine(pos = p, angle = 90, movable = False)
            self.graph.addItem(l)  
        
        # display holdoff  
        for p in sel_hold:
            l = pg.InfiniteLine(pos = p + self.holdoff_box.value(), angle = 90, movable = False, pen = pg.mkPen(color=(200, 200, 255), style = QtCore.Qt.DotLine))
            self.graph.addItem(l) 


# When called, this automatically rescales the graph to fit the data plus
# a padding factor. The padding factor is fetched from the "zoom" slider in the
# GUI. This function is fairly slow and should only be called periodically. By 
# default, it's only called once a complete sample period has elapsed. 
def graph_fit(self):
    self.graph_padding_factor = self.graph_zoom_slider.value() / 100
    high = max(self.value_history)
    low  = min(self.value_history)
    pad  = math.floor(((high) - (low)) * self.graph_padding_factor)
    sps = self.value_history_timed[::-1][0][1] - self.value_history_timed[0][1]
    if(sps == 0):
        return
    print("PAD VALUE: " + str(pad))
    self.statusBar.showMessage("Samples per second: " + str(math.floor((self.value_history_max / sps) * 1000)))
    self.graph.setRange(
        xRange = (0, self.value_history_max), 
        yRange = (high + pad , low - pad)
    )

