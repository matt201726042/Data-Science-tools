from re import T
import numpy as np
from scipy.interpolate import PchipInterpolator
import bisect
import time
import vispy
from vispy import app, visuals, scene
from vispy.scene import visuals
from vispy import app
from vispy.util.quaternion import Quaternion
import sys

import stocks as s

#############################################
vispy.use("glfw")
canvas = vispy.scene.SceneCanvas(keys='interactive', title='Forecaster', show=True)
canvasTwo = vispy.scene.SceneCanvas(keys='interactive', title='Backtester', show=True)
view = canvas.central_widget.add_view()
view.camera = 'fly'
#############################################
#This model has no temporal communication, each prediction is independent of every other prediction.
#1) USE QTHREAD
#2) Note that if the input time dimension is not regularly distributed, the bin graph will draw out of place under the assumption of a regular distribution for optimisation purposes
#############################################
Plot3D = scene.visuals.create_visual_node(vispy.visuals.line_plot.LinePlotVisual)
scatter = visuals.Markers()
view.add(scatter)
scatterBase = Plot3D()
view.add(scatterBase)
scatterBinned = Plot3D()
view.add(scatterBinned)
#view.camera = scene.TurntableCamera(up='z')
axis = visuals.XYZAxis(parent=view.scene)

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
        pchips.append(PchipInterpolator(dataDiff[0], dataDiff[dim], extrapolate=False))
    timeRange = np.amax(dataDiff[0]) - np.amin(dataDiff[0])
    disps = np.linspace(-timeRange, timeRange, phaseSamples)
    dists = []
    allDists = []
    dataSims = []
    lens = []
    for s in range(phaseSamples):
        dataSim = dataDiff.copy()
        dataSim[0] += disps[s]
        dataSims.append(dataSim)
        tempDists = []
        for i in range(dataLen-1):
            if dataDiff[0][0] <= dataSim[0][i] <= dataDiff[0][-1]:
                dimDists = []
                for dim in range(1,dataDims):
                    dimDists.append(np.abs(pchips[dim-1](dataSim[0][i]) - dataDiff[dim][i]) ** 2)
                tempDists.append(sum(dimDists) ** 0.5)
        lens.append(len(tempDists))
        allDists.extend(tempDists)
        dists.append(np.mean(tempDists))
        #print(np.round(s/phaseSamples, 2))
    maxDist = max(allDists)
    maxLen = dataLen - 1
    out = [[] for i in range(dataDims + 1)]
    for s in range(phaseSamples):
        weight = 1 - ((dists[s]/maxDist) + (1 - (lens[s]/maxLen)))
        for i in range(dataLen-1):
            bisec = bisect.bisect(out[0], dataSims[s][0][i])
            for dim in range(dataDims):
                out[dim].insert(bisec, dataSims[s][dim][i])
            out[-1].insert(bisec, weight)
        #print(tempDistsMean)
        #print(np.round(s/phaseSamples, 2))
	
    idx = np.where((out[0]<dataDiff[0][-1])*(out[0]>dataDiff[0][0]))[0]	
    binCount = len(data[0]) #how many bins?
    binCount -= 2 #remove 2 because 2 inner border cases are added
    binWidth = (timeRange * 2) / binCount
    #np.aspace(0,idx[0], idx[0]//(binCount/2)).astype(int)
    #np.aspace(idx[-1], len(out[0])-1, ((len(out[0])-1) - idx[-1])//(binCount/2))
    binBounds = [list(np.arange(0,idx[0], idx[0]//(binCount/2)).astype(int)), list(np.arange(idx[-1], len(out[0])-1, ((len(out[0])-1) - idx[-1])//(binCount/2)).astype(int))]
    binBounds[0].append(idx[0])
    binBounds[1].append(len(out[0])-1)
    binOut = [[[] for dim in range(dataDims)], [[] for dim in range(dataDims)]]
    undiff = [[] for dim in range(dataDims)]
    for side in range(2):
        for dim in range(dataDims-1,-1,-1):
            #undifferencing (discrete integration)
            if dim > 0:
                for bin in range(len(binBounds[dim])-1): #binning
                    #try:
                    binOut[side][dim].append(np.average(out[dim][binBounds[side][bin]:binBounds[side][bin+1]], weights=np.array(out[-1][binBounds[side][bin]:binBounds[side][bin+1]])**100) * binWidth)
                    #except Exception as e:
                    #print(e, "FAIL", binBounds[side][bin], binBounds[side][bin+1])
                    #binOut[side][dim].append(0)
                if side == 0: #pre center
                    temp = binOut[side][dim]
                    a = data[dim][0]
                    undiff[dim].append(a)
                    for i in range(len(temp)):
                        a -= temp[i]
                        undiff[dim].append(a)#.insert(-1, a)
                    undiff[dim] = undiff[dim][::-1]
                    undiff[0].extend(list(np.linspace(dataDiff[0][0] - timeRange, dataDiff[0][-1] - timeRange, len(binOut[0][1])+1))[:-1])
                    undiff[0].append(data[0][0])
                elif side == 1: #post center
                    temp = binOut[side][dim]
                    b = data[dim][-1]
                    undiff[dim].append(b)
                    for i in range(len(temp)):
                        b += temp[i]
                        undiff[dim].append(b)
                    undiff[0].append(data[0][-1])
                    undiff[0].extend(list(np.linspace(dataDiff[0][0] + timeRange, dataDiff[0][-1] + timeRange, len(binOut[1][1])+1))[1:])

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

    #print("fps", np.round(1 / (time.perf_counter() - startTime),2))
    return undiff

if __name__ == "__main__":
    global t
    global out
    t = -0.0001
    out = []
    stockData = s.getStockData()
    stockData = stockData[::int(np.ceil(len(stockData)/2000000))]
    stockData -= np.mean(stockData)
    stockData /= (np.amax(stockData) / 10)
    def update(ev):
        global t
        global stockData
        if t < 0:
            view.camera.center = [0,0,30]
            view.camera.rotation1 = Quaternion.create_from_euler_angles(*[0,0,0], degrees=True)
            view.camera.scale_factor = 1
        if t < len(stockData)-4:
            t += 1
            #data = [np.linspace(0,10,15), +np.cos(np.linspace(0+t,10+t,15))+np.sin(np.linspace(0+t,20+t,15))]
            #data = [np.linspace(-10,10,int(t+3)), stockData[:int(t+3)]]
            data = [np.linspace(-10,10,int(len(stockData))), stockData]
            out = forecaster(data, 30)
            out = np.transpose(out)
        
            cnct = [[i, i+1] for i in range(len(out) - 1)]
            del cnct[(len(cnct)//2)]
            scatterBase.set_data(np.transpose(data), connect=np.array([[i, i+1] for i in range(len(data[0]) - 1)]), color=(1, 1, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=3, face_color=(0.5, 0.5, 1, 0)) #np.zeros(np.size(DATA, 1))
            scatterBinned.set_data(out, connect=np.array(cnct), color=(0.5, 0.5, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=2, face_color=(0.5, 0.5, 1, 0))
            timer.stop()

    timer = app.Timer()
    timer.connect(update)
    timer.start(0.25)
    if sys.flags.interactive == 0:
        canvas.show()
        app.run()