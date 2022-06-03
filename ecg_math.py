import numpy, math
from scipy import signal
import statistics as stat

# detect peaks using scipy. 
#   prominence: the threshold the peak needs to be at, relative to the surrounding samples
#   distance  : (AKA holdoff) minimum required distance between the previous peak to the next peak
#   height    : minimum height of peak to be accepted
# modifies:  stores index of peaks in self.peaks 
# returns :  center (not average) of recorded values
def detect_peaks(self, sig_prominence = 20, sig_distance = 60):
    center = (max(self.value_history) - ((max(self.value_history) - min(self.value_history)) / 2))
    self.peaks = signal.find_peaks(
                self.value_history, 
                prominence = self.prominence_box.value(),
                height = center,
                distance = self.holdoff_box.value(),
            )[0]
    return center
    
    
# Update the heart rate LCD reading. 
# Converts the average time between peaks to frequency 
# (1 / (<avg peak distance> * <capture rate in ms>)) * 60 * 1000
def update_hr(self):

    # If the system is in the calibration cycle, it won't have enough datapoints to do this function
    if(self.calibrating > 0):
        return
        
    self.detect_peaks()
    times = list()
    if(len(self.peaks) > 1):
        for i, v in enumerate(self.peaks):
            if(i != 0):
                last = self.value_history_timed[self.peaks[i - 1]][1]
                times.append(self.value_history_timed[v][1] - last)
    if(len(times)):
        f = (1 / (sum(times) / len(times)))
        rate = f * 1000 * 60
        self.lcdNumber.display(rate)

        # update heart rate history
        self.rate_alarm_history.append(rate)
        self.rate_alarm_history.pop(0)
        
        # check if rate alarm has been tripped or reset, this should probably be moved 
        avg = math.floor(stat.mean(self.rate_alarm_history))
        if(self.rate_alarm_active == False):
            if(avg > self.high_limit_box.value()):
                self.rate_alarm_active = True
                self.alarm_on("MAX RATE ALARM")
            if(self.low_limit_box.value() > avg):
                self.rate_alarm_active = True
                self.alarm_on("MIN RATE ALARM")     # placeholder
        else:
            if(avg <= self.high_limit_box.value() and self.low_limit_box.value() <= avg):
                self.rate_alarm_active = False 
                self.alarm_off()
    else:
        self.lcdNumber.display(0)
