import numpy as np
import pandas as pd
import hrv
from hrv.filters import moving_average


def RRints(dat):
    dat[1].replace('B', 1, inplace=True)
    dat[1].replace(' ', 0, inplace=True)
    # convert the B's, which indicate heart beats, to 1

    rr_intervals = []
    for i in range(0, len(dat[1])):
        if dat[1][i] == 1:
            rr_intervals.append(dat[0][i])
            dat[1][i+1] = 0
    # remove the second B

    rr = []
    for i in range(1, len(rr_intervals)):
        rrint = 1000.0 * (rr_intervals[i] - rr_intervals[i-1]) / 60.0
        rr.append(rrint)
    # the rr intervals

    return rr


resting_b = pd.read_csv("/Users/mouritsdebeer/Desktop/control1.txt", header=None)

print(resting_b)

rr = RRints(resting_b)

print(rr)

print(np.average(rr))


filt_rri = moving_average(np.array(rr), order = 3)

print(filt_rri)

