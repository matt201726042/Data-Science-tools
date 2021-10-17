import numpy as np
from scipy.interpolate import PchipInterpolator
def forecaster(data, phaseSamples):
    dataDims = np.size(data, axis=0)
    dataLen = np.size(data[0], axis=0)
    dataDiff = []
    dataDiff.append([np.mean([data[0][i], data[0][i+1]]) for i in range(dataLen-1)])
    timeDiff = np.diff(data[0], n=1)
    pchips=[]
    for dim in range(1,dataDims):
        dataDiff.append(np.diff(data[dim], n=1) / timeDiff)
        pchips.append(PchipInterpolator(dataDiff[0], dataDiff[dim]))
    dimRange = np.amax(dataDiff[0]) - np.amin(dataDiff[0])
    disps = np.linspace(-dimRange, dimRange, phaseSamples)
    dists = []
    allDists = []
    lens = []
    dataSims = []
    for s in range(phaseSamples):
        dataSim = dataDiff
        dataSim[0] += disps[s]
        dataSims.append(dataSim)
        tempDists = []
        for i in range(dataLen-1):
            if dataDiff[0][0] <= dataSim[0][i] <= dataDiff[0][-1]:
                dimDists = []
                for dim in range(1,dataDims):
                    dimDists.append(np.abs(pchips[dim-1](dataSim[0][i]) - dataDiff[dim][i]) ** 2)
            dDist = (sum(dimDists) ** 0.5)
            tempDists.append(dDist)
        allDists.extend(tempDists)
        dists.append(np.mean(tempDists))
        lens.append(len(tempDists))
    maxDist = max(allDists)
    maxLen = max(lens)
    for s in range(phaseSamples):
        weight = (dists[s]/maxDist) + (1 - (lens[s]/maxLen))
        for i in range(dataLen-1):
            
        #print(tempDistsMean)
        print(s/phaseSamples)
    
    #kernel moving average

data = [np.linspace(0,1,2000), np.linspace(0,1,2000)]
forecaster(data, 6000)