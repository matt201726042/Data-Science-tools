import numpy as np
from scipy.interpolate import PchipInterpolator
import bisect
import time
def forecaster(data, phaseSamples):
    startTime = time.perf_counter()
    dataDims = np.size(data, axis=0)
    dataLen = np.size(data[0], axis=0)
    dataDiff = []
    dataDiff.append([np.mean([data[0][i], data[0][i+1]]) for i in range(dataLen-1)])
    timeDiff = np.diff(data[0], n=1)
    pchips=[]
    for dim in range(1,dataDims):
        dataDiff.append(np.diff(data[dim], n=1) / timeDiff) #differencing (discrete differentiation)
        pchips.append(PchipInterpolator(dataDiff[0], dataDiff[dim]))
    dimRange = np.amax(dataDiff[0]) - np.amin(dataDiff[0])
    disps = np.linspace(-dimRange, dimRange, phaseSamples)
    dists = []
    allDists = []
    dataSims = []
    lens = []
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
        lens.append(len(tempDists))
        allDists.extend(tempDists)
        dists.append(np.mean(tempDists))
        #print(np.round(s/phaseSamples, 2))
    maxDist = max(allDists)
    maxLen = dataLen - 1
    out = [[] for i in range(dataDims + 1)]
    for s in range(phaseSamples):
        weight = (dists[s]/maxDist) + (1 - (lens[s]/maxLen))
        for i in range(dataLen-1):
            bisec = bisect.bisect(out[0], dataSims[s][0][i])
            for dim in range(dataDims):
                out[dim].insert(bisec, dataSims[s][dim][i])
            out[-1].insert(bisec, weight)
        #print(tempDistsMean)
        #print(np.round(s/phaseSamples, 2))
	
    idx = np.where((out[0]<dataDiff[0][-1])*(out[0]>dataDiff[0][0]))[0]	
    binCount = 15
    binCount -= 2
    #np.aspace(0,idx[0], idx[0]//(binCount/2)).astype(int)
    #np.aspace(idx[-1], len(out[0])-1, ((len(out[0])-1) - idx[-1])//(binCount/2))
    binBounds = [list(np.arange(0,idx[0], idx[0]//(binCount/2)).astype(int)), list(np.arange(idx[-1], len(out[0])-1, ((len(out[0])-1) - idx[-1])//(binCount/2)).astype(int))]
    binBounds[0].append(idx[0])
    binBounds[1].append(len(out[0])-1)
    binOut = [[[] for dim in range(dataDims)], [[] for dim in range(dataDims)]]
    undiff = [[[] for dim in range(dataDims)], [[] for dim in range(dataDims)]]
    for side in range(2):
        for dim in range(dataDims):
            #undifferencing (discrete integration)
            if dim > 0:
                for bin in range(len(binBounds[dim])-1): #binning
                    #try:
                    binOut[side][dim].append(np.average(out[dim][binBounds[side][bin]:binBounds[side][bin+1]], weights=out[-1][binBounds[side][bin]:binBounds[side][bin+1]]))
                    #except Exception as e:
                        #print(e, "FAIL", binBounds[side][bin], binBounds[side][bin+1])
                        #binOut[side][dim].append(0)
                if side == 0: #pre center
                    temp = binOut[side][dim]
                    a = data[dim][0]
                    undiff[0][dim].append(a)
                    for i in range(len(temp)-1,-1,-1):
                        a += temp[i]
                        undiff[0][dim].insert(-1, a)
                elif side == 1: #post center
                    temp = binOut[side][dim]
                    b = data[dim][-1]
                    undiff[1][dim].append(b)
                    for i in range(len(temp)):
                        b += temp[i]
                        undiff[1][dim].append(b)
            else:
                undiff[side][0] = binBounds[side]
        #undiff[side] = np.transpose(undiff[side])

    # #kernel moving average
    # binWidth = (dataDiff[0][-1] - dataDiff[0][0]) / 100
    # dataDiffDiff = np.diff(dataDiff[0], n=1)
    # outSmooth = []
    # lenOut = len(out[0])
    # for i in range(len(out[0])):
    #     idx = np.where((out[0]<=(out[0][i] + binWidth))*(out[0]>=(out[0][i] - binWidth)))[0]
    #     sums = [0 for i in range(dataDims)]
    #     weights = [0 for i in range(dataDims)]
    #     if i % 100 == 0:
    #         print(i/lenOut)
    #     for j in range(len(idx)):
    #         for dim in range(dataDims):
    #             sums[dim] += out[dim][idx[j]] * out[-1][idx[j]]
    #             weights[dim] += out[-1][idx[j]]
    #     outSmooth.append(np.array(sums) / np.array(weights))

    print(undiff)
    print("fps", 1 / (time.perf_counter() - startTime))
    return undiff

data = [np.linspace(0,10,20), np.sin(np.linspace(0,10,20))]
forecaster(data, 600)