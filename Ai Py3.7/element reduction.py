import numpy as np
from scipy.interpolate import PchipInterpolator
import random
import matplotlib.pyplot as plt
import time
from matplotlib.widgets import Slider, Button, RadioButtons
figure = plt.figure() #gcf()

def evenDistribution(bounds, seps):
    seps = round(seps)
    result = []
    for sep in range(seps):
        boundRange = bounds[1] - bounds[0]
        if seps > 1:
            queryPar = ((1 / (seps - 1)) * sep * boundRange) + bounds[0]
        else:
            queryPar = sum(bounds) / 2
        result.append(queryPar)
    return result

timeDATA = np.array([])
valueDATA = np.array([])

initialValueDATA = np.array([])
counterOne = 10
for i in range(counterOne):
    temp = random.uniform(0, 1)
    initialValueDATA = np.append(initialValueDATA, temp)

initialInterpolator = PchipInterpolator([i + random.uniform(-0.49, 0.49) for i in range(len(initialValueDATA))], initialValueDATA)
counterTwo = 5000
for i in range(counterTwo):
    timeDATA = np.append(timeDATA, i + random.uniform(-0.49, 0.49))
    valueDATA = np.append(valueDATA, initialInterpolator((counterOne / counterTwo) * (i + 1)))

historicDiff = np.array([])
historicRed = np.array([])
historicEff = np.array([])

for i in range(round(counterTwo)): #round(counterTwo / 2) - 1, round(counterTwo / 2) #counterTwo
    i += 1
    secondDifference = np.abs(np.diff(valueDATA, n=2)) + 0.000000001
    cumsum = np.cumsum((np.abs(secondDifference)))
    cumsum = np.average(np.array([cumsum, evenDistribution([0, cumsum[-1]], len(cumsum))]), axis=0, weights=[counterTwo - i - 1, i - 1])
    cumsumInterpolator = PchipInterpolator(cumsum, evenDistribution([timeDATA[0], timeDATA[-1]], len(cumsum)))
    times = cumsumInterpolator(evenDistribution([cumsum[0], cumsum[-1]], i), extrapolate=True)
    inputInterpolator = PchipInterpolator(timeDATA, valueDATA, extrapolate=True)
    x = times
    y = inputInterpolator(times)
    if i > 1:
        outputInterpolator = PchipInterpolator(x, y)
        combinedTimes = np.concatenate((x, timeDATA), axis=0)
        historicDiff = np.append(historicDiff, np.mean(np.abs(outputInterpolator(combinedTimes) - inputInterpolator(combinedTimes))))
        historicDiffPerc = (100 * (np.mean([np.abs(np.round(historicDiff[i]) - historicDiff[i]) for i in range(len(historicDiff))]) / (max(historicDiff) - min(historicDiff))))
        historicRed = np.append(historicRed, 100 - ((len(times) / (len(timeDATA))) * 100))
        historicEff = np.append(historicEff, np.abs(historicRed[-1] / historicDiffPerc)) #historicRed[-1] #historicDiffPerc
        #print((100 * (np.mean([abs(round(historicDiff[i]) - historicDiff[i]) for i in range(len(historicDiff))]) / (max(historicDiff) - min(historicDiff)))))
        #print(i, "     ", historicDiff[-1])

    plt.clf()
    if np.size(historicRed) == 0:
        tempHistoricRed = 0
        tempHistoricDiffPerc = 0
        tempHistoricEff = 0
    else:
        tempHistoricRed = historicRed[-1]
        tempHistoricEff = historicEff[-1]
        tempHistoricDiffPerc = historicDiffPerc
        scaledOne = (historicDiff[-50:] * ((max(valueDATA) - min(valueDATA)) / (max(historicDiff[-50:]) - min(historicDiff[-50:]))))[-50:]
        scaledTwo = (historicDiff * ((max(valueDATA) - min(valueDATA)) / (max(historicDiff) - min(historicDiff))))
        scaledThree = (historicEff * ((max(valueDATA) - min(valueDATA)) / (max(historicEff) - min(historicEff))))
        plt.plot((counterTwo / 100) * (100 - historicRed[-50:]), scaledOne - max(scaledOne), color='black', label='zoomed difference')
        plt.plot((counterTwo / 100) * (100 - historicRed), scaledTwo - max(scaledTwo), color='orange', label='difference')
        plt.plot((counterTwo / 100) * (100 - historicRed), scaledThree - max(scaledThree), color='green', label='efficiency')
    plt.plot(x, y, linewidth=0.75, marker='o', markerfacecolor='black', markeredgecolor='white', color='blue', alpha=1, label=str(i) + "   " + str(np.round(tempHistoricEff, 2)) + " efficiency   " + str(np.round(tempHistoricRed, 2)) + "% reduction   " + str(round(tempHistoricDiffPerc, 10)) + "% loss")
    plt.plot(timeDATA, valueDATA, color='black', linewidth=1.5, alpha=0.25)
    tempScaled = secondDifference * ((max(valueDATA) - min(valueDATA)) / (max(secondDifference) - min(secondDifference)))
    plt.plot(evenDistribution([timeDATA[0], timeDATA[-1]], len(secondDifference)), (tempScaled - max(tempScaled)), color='blue', linewidth=0.25)
    plt.legend()
    plt.draw()
    plt.pause(0.000001)
    #plt.pause(1)
plt.show()