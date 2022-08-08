import pyqtgraph as pg
from PyQt5 import QtWidgets, uic, QtCore, QtWidgets
import statistics as stat
from scipy.signal import savgol_filter
from ecg_viewer_window import Ui_MainWindow
import math, numpy


# Clear and refresh graph. pyqtgraph works a lot like a frame buffer, so
# the graph must be cleared before it's redrawn.
def draw_graph(self):
    try:
        fdat = savgol_filter(
            self.value_history,
            window_length = self.window_length_box.value(),
            polyorder = self.polyorder_box.value(),
            mode = 'interp',
            )[25:self.value_history_max - 25]
    except Exception as e:
        self.window_length_box.setValue(99)
        self.polyorder_box.setValue(9)
        print(e)
    self.curve.setData(numpy.arange(fdat.size), fdat, skipFiniteCheck = True)


    # Visually shows signal tracking information. VERY SLOW IF ENABLED
    if(self.show_track.isChecked()):
        mean = self.value_history.mean()
        center = self.detect_peaks()
        self.graph.clear()
        self.graph.plot(numpy.arange(self.value_history.size), self.value_history, skipFiniteCheck = True)
        center_line = pg.InfiniteLine(pos = center, angle = 0, movable = False, pen = self.yellow_pen)
        self.graph.addItem(center_line)
        mean_line = pg.InfiniteLine(pos = mean, angle = 0, movable = False, pen = self.red_pen)
        self.graph.addItem(mean_line)

        # select datapoints to graph depending on if the capture is actively running or not
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
    high = self.value_history.max()
    low  = self.value_history.min()
    pad  = math.floor(((high) - (low)) * self.graph_padding_factor)
    sps = self.time_history[::-1][0] - self.time_history[0]
    if(sps == 0):
        return
    print("PAD VALUE: " + str(pad))
    self.statusBar.showMessage("Samples per second: " + str(math.floor((self.value_history_max / sps) * 1000)))
    self.graph.setRange(
        xRange = (0, self.value_history_max),
        yRange = (high + pad , low - pad)
    )


def bold_toggle(self):
    if(self.bold_checkBox.isChecked()):
        self.green_pen = pg.mkPen('g', width = 2)
    else:
        self.green_pen = pg.mkPen('g', width = 1)
    self.graph.clear()
    self.curve = self.graph.plot(numpy.arange(self.value_history.size), self.value_history, pen = self.green_pen, skipFiniteCheck = True)
