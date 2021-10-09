from scipy import signal
import numpy as np
from scipy.interpolate import PchipInterpolator
import numpy as np
import vispy
from vispy import app, visuals, scene
from vispy.scene import visuals
from vispy import app
import sys
import random
import math
import bisect

canvas = vispy.scene.SceneCanvas(keys='interactive', title='plot3d', show=True)
view = canvas.central_widget.add_view()
view.camera = 'fly'

#############################################

def ndEvenDist(ndBounds, count):
    z = np.array([[np.linspace(ndBounds[dim][param][0].astype(np.float), ndBounds[dim][param][1].astype(np.float), num=math.ceil(count ** (1 / np.size(ndBounds, axis=0))), endpoint=True, retstep=False, dtype=None, axis=0) for param in range(np.size(ndBounds[dim], axis=0))] for dim in range(np.size(ndBounds, axis=0))])
    z = z.reshape(-1, z.shape[-1])
    meshgrid = np.meshgrid(*z)
    meshgrid = [meshgrid[i].flatten() for i in range(np.size(meshgrid, axis=0))]
    return [meshgrid[a][list(set(np.floor(np.linspace(0, len(meshgrid[a]), num=count + 2, endpoint=True, retstep=False, dtype=None, axis=0)[1:-1]).astype(int)))] for a in range(len(meshgrid))]

#############################################


def main(DATA, signalSamples, phaseSamples, binCount):
    DATA = DATA.astype(np.float)
    DATAdims = len(DATA)


    ndBounds = []
    pchips = []
    binBounds = []
    bins = []
    for dim in range(np.size(DATA, axis=0)):
        dimRange = np.amax(DATA[dim]) - np.amin(DATA[dim])
        ndBounds.append([[-dimRange, dimRange]])
        if dim > 0:
            pchips.append(PchipInterpolator(DATA[0], DATA[dim]))
        else:
            binBounds = np.linspace(-dimRange + DATA[0][0], dimRange + DATA[0][-1], binCount+1, endpoint=True)
            bins = [[] for i in range(len(binBounds)-1)]
    sims = ndEvenDist(ndBounds, phaseSamples)
    
    result = {"data":[], "weights":[], "lens":[]}
    for s in range(np.size(sims[0])):
        tempDATA = DATA.copy()
        simParams = [sims[0][s], sims[1][s]]
        for d in range(len(simParams)):
            tempDATA[d] += simParams[d]
        result["data"].append(tempDATA)

        tempDists = []
        for i in range(len(tempDATA[0])):
            if not(bisect.bisect_right(DATA[0], tempDATA[0][i]) == 0 or bisect.bisect_left(DATA[0], tempDATA[0][i]) == len(DATA[0])):
                dimDists = []
                for d in range(1, len(simParams)):
                    dimDists.append(abs(pchips[d-1](tempDATA[0][i]) - tempDATA[d][i]) ** 2)
                dDist = (sum(dimDists) ** 0.5)
                tempDists.append(dDist)
        tempDistsMean = np.mean(tempDists)
        for i in range(len(tempDATA[0])):
            b = bisect.bisect(binBounds, tempDATA[0][i])
            lenPerc = len(tempDists)/(len(DATA[0]) - 1)
            if len(tempDists) != 0 and not(b == 0 or b == binCount+1):
                bins[b-1].append([[tempDATA[a][i] for a in range(1,DATAdims)], (((1-tempDistsMean) + lenPerc)/2) + 1])
        result["weights"].append(tempDistsMean)
        result["lens"].append(lenPerc)
    result["binned"] = [[] for d in range(DATAdims-1)]
    result["binLocs"] = [np.mean([binBounds[i], binBounds[i+1]]) for i in range(binCount)]
    for b in range(len(bins)):
        count = [0 for i in range(DATAdims)]
        total = [0 for i in range(DATAdims)]
        #bestWeight = 0
        #bestValue = [0 for i in range(DATAdims)]
        for i in range(len(bins[b])):
            for d in range(DATAdims-1):
                total[d] += bins[b][i][0][d] * (bins[b][i][1]**100)
                count[d] += (bins[b][i][1]**100)
            #if bins[b][i][1] > bestWeight:
                #bestWeight = bins[b][i][1]
                #bestValue = bins[b][i][0]
        for d in range(DATAdims-1):
            try:
                result["binned"][d].append(total[d] / count[d])
                #result["binned"][d].append(bestValue[d])
            except:
                result["binned"][d].append(0)
    result["lens"] = np.array(result["lens"]).astype(np.float)
    result["weights"] = np.array(result["weights"])
    result["weights"] -= np.amin(result["weights"])
    result["weights"] /= np.amax(result["weights"])
    result["weights"] = ((1-result["weights"]) + result["lens"]) / 2 #1 - (((1 - ((1 - result["weights"]) ** 1)) + (1-result["lens"])) / 2)
    return result

Plot3D = scene.visuals.create_visual_node(vispy.visuals.line_plot.LinePlotVisual)


scatter = visuals.Markers()
view.add(scatter)
scatterBase = Plot3D()
view.add(scatterBase)
scatterBinned = Plot3D()
view.add(scatterBinned)

#view.camera = scene.TurntableCamera(up='z')

# just makes the axes
axis = visuals.XYZAxis(parent=view.scene)


t = 0
def update(ev):
    global scatter
    global scatterBase
    global t
    t += 0.1
    #DATA = [np.linspace(0, 1, 50), np.array([np.sin(x) + (random.uniform(0,1) / 10) for x in np.linspace(t,t+8,50)])]
    #DATA = [[1,2,3], [1,2,3]]
    #scatter.set_data(predictor(DATA, 25), edge_color="red", face_color=(1, 1, 1, .5), size=5)
    DATA = np.array([np.linspace(0, 1, 10), np.array([np.sin(x) + ((x-t)/1500000) + (random.uniform(0,0) / 10) for x in np.linspace(t,t+8,10)])])
    DATAdim = len(DATA)


    binCount = 30
    out = main(DATA, 10, 650, binCount) #signalSamples, phaseSamples, binCount


    weights = np.array([np.full((len(out["data"][0][0])), w) for w in out["weights"]]).flatten()
    colours = []
    for w in weights:
        colours.append([1-w,w/2,w,w])
    outData = np.array([np.transpose(out["data"][i]) for i in range(len(out["data"]))])
    outDataShape = np.shape(outData)
    outData = outData.reshape(outDataShape[0] * outDataShape[1], outDataShape[2])
    binData = []
    binData.append(out["binLocs"])
    for a in range(DATAdim-1):
        binData.append(out["binned"][a])
    binData = np.transpose(np.array(binData))
    #print("A", len(binData[0]), len(binData[1]), np.transpose(np.array(binData)), "A")
    try:
        scatter.set_data(outData[:100000], edge_color="black", face_color=colours[:100000], size=4)

        #scatterBase.set_data(pos=self.out[0], connect=self.out[1], width=1000, color=(0.5, 0.5, 1, 1))
        scatterBase.set_data(np.transpose(DATA + np.zeros(np.size(DATA, 1))), connect=np.array([[i, i+1] for i in range(len(DATA[0]) - 1)]), color=(1, 1, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=3, face_color=(0.5, 0.5, 1, 0))
        scatterBinned.set_data(binData, connect=np.array([[i, i+1] for i in range(binCount - 1)]), color=(0.5, 0.5, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=1, face_color=(0.5, 0.5, 1, 0))
    except:
        pass

timer = app.Timer()
timer.connect(update)
timer.start(0)
if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()