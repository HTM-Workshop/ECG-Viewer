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
import statistics as stat
from scipy import signal

def math_calc_sps(self) -> int:
    """
    Returns the samples per second based on the capture period time range.
    This should be called a the end of the capture period.
    """

    sample_time_range = self.time_history[-1] - self.time_history[0]
    return math.floor((self.value_history_max / sample_time_range) * 1000)
    

def math_detect_peaks(self) -> float:
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


def math_update_hr(self) -> None:
    """
    Update the heart rate LCD reading.\n
    Converts the average time between peaks to frequency.
    """

    times = []
    if len(self.peaks) > 1:
        for i, value in enumerate(self.peaks):
            if i:
                last = self.time_history[self.peaks[i - 1]]
                times.append(self.time_history[value] - last)
    if len(times) > 1:
        freq = (1 / (sum(times) / len(times)))
        rate = freq * 1000 * 60

        # update heart rate history
        self.rate_alarm_history.append(rate)
        self.rate_alarm_history.pop(0)

        # display rate as average of rate history
        self.lcdNumber.display(math.floor(stat.mean(self.rate_alarm_history)))

        # check if rate alarm has been tripped or reset, this should probably be moved
        avg = math.floor(stat.mean(self.rate_alarm_history))

        self.ui_clear_message()
        if avg > self.high_limit_box.value():
            self.rate_alarm_active = True
            self.ui_alarm_on("MAX RATE ALARM")
        if self.low_limit_box.value() > avg:
            self.rate_alarm_active = True
            self.ui_alarm_on("MIN RATE ALARM")
        if self.rate_alarm_active:
            if(avg <= self.high_limit_box.value() and self.low_limit_box.value() <= avg):
                self.rate_alarm_active = False
                self.ui_alarm_off()
    else:
        self.lcdNumber.display(0)
        self.ui_set_message("SIGNAL LOSS")