from scipy import signal
import numpy as np
from scipy.interpolate import PchipInterpolator
import numpy as np
import vispy
import vispy.scene
from vispy.scene import visuals
from vispy import app
import sys

def weightedAvgConvolve(first, second):
    convOne = signal.convolve(first, second)
    convTwo = signal.convolve([1 for i in range(len(first))], second)
    return convOne, convTwo  # np.divide(convOne, convTwo) #

def autocorr(x):
    diffs = np.array([])
    for lag in range(x.size - 1):
        diffs = np.append(diffs, (1 / (np.mean(np.absolute(x[:x.size - lag - 1] - x[lag + 1:])) + 1) ** 2))
    diffs = np.insert(diffs, 0, 1)
    diffs = np.insert(diffs, 0, diffs[1:][::-1])
    return diffs

def predictor(DATA, samples):
    DATA = np.array(DATA)
    tempDATA = np.zeros((2, samples))
    autocorrs = np.zeros((2, (samples * 2) - 1))

    if samples != DATA[0].size:
        for dim in range(2):
            pchip = PchipInterpolator(np.arange(1, DATA[1 - dim].size + 1), DATA[dim])
            tempDATA[dim] = pchip(np.linspace(1, DATA[dim].size, samples))
            autocorrs[dim] = autocorr(tempDATA[dim])
    else:
        tempDATA = DATA
        for dim in range(2):
            autocorrs[dim] = autocorr(tempDATA[dim])

    rowCount = autocorrs[1].size
    rows = []
    divisors = []
    predictLen = (samples * 3) - 2
    for row in range(rowCount):
        print(autocorr(tempDATA[1] + row - span))
    for row in range(rowCount):
        result = weightedAvgConvolve(tempDATA[1] + row - ((rowCount - 1) / 2), np.abs(autocorrs[0] - autocorrs[1][row]))
        print(np.abs(autocorrs[0] - autocorrs[1][row]))
        rows.append(result[0])
        divisors.append(result[1])
    span = tempDATA[0][-1] - tempDATA[0][0]
    rowsSum = np.sum(rows, axis=0) #np.divide(np.sum(rows, axis=0), np.array([((x - (predictLen / 2)) + 1) ** 0.2 for x in range(predictLen)]))
    x = np.linspace(tempDATA[0][0] - span, tempDATA[0][-1] + span, predictLen)
    y = rowsSum / np.sum(divisors, axis=0)
    z = [0 for x in range(predictLen)]
    return np.array([[x[i], y[i], z[i]] for i in range(x.size)])

print(predictor([[1,2,3], [1,2,3]], 3))