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

import math
import numpy
import statistics as stat
from scipy import signal


def detect_peaks(self, sig_prominence: int = 20, sig_distance: int = 60) -> float:
    """
    Detects peaks using scipy. 

    Operands:
        prominence: the threshold the peak needs to be at, relative to the surrounding samples
        distance  : (AKA holdoff) minimum required distance between the previous peak to the next peak
        height    : minimum height of peak to be accepted\n
    modifies:  stores index of peaks in self.peaks 
    returns :  center (not average) of recorded values    
    """

    vmax: int = self.value_history.max()
    vmin: int = self.value_history.min()
    center: float = (vmax - (vmax - vmin) / 2)
    self.peaks = signal.find_peaks(
                self.value_history, 
                prominence = self.prominence_box.value(),
                height = center,
                distance = self.holdoff_box.value(),
            )[0]
    return center
    

def update_hr(self) -> None:
    """
    Update the heart rate LCD reading.\n
    Converts the average time between peaks to frequency.
    """
    
    times = list()
    if(len(self.peaks) > 1):
        for i, v in enumerate(self.peaks):
            if(i != 0):
                #last = self.value_history_timed[self.peaks[i - 1]][1]
                last = self.time_history[self.peaks[i - 1]]
                #times.append(self.value_history_timed[v][1] - last)
                times.append(self.time_history[v] - last)
    if(len(times)):
        f = (1 / (sum(times) / len(times)))
        rate = f * 1000 * 60

        # update heart rate history
        self.rate_alarm_history.append(rate)
        self.rate_alarm_history.pop(0)
        
        # display rate as average of rate history
        self.lcdNumber.display(math.floor(stat.mean(self.rate_alarm_history)))
        
        # check if rate alarm has been tripped or reset, this should probably be moved 
        avg = math.floor(stat.mean(self.rate_alarm_history))

        self.clear_message()
        if(avg > self.high_limit_box.value()):
            self.rate_alarm_active = True
            self.alarm_on("MAX RATE ALARM")
        if(self.low_limit_box.value() > avg):
            self.rate_alarm_active = True
            self.alarm_on("MIN RATE ALARM")
        if(self.rate_alarm_active == True):
            if(avg <= self.high_limit_box.value() and self.low_limit_box.value() <= avg):
                self.rate_alarm_active = False 
                self.alarm_off()
    else:
        self.lcdNumber.display(0)
        self.set_message("SIGNAL LOSS")

