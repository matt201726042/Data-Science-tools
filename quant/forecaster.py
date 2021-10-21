def multiprocessing_func(Global, id, t):
    from scipy import signal
    from scipy.spatial.transform import Rotation as R
    import numpy as np
    from scipy.interpolate import PchipInterpolator
    import numpy as np
    import vispy
    from vispy import app, visuals, scene
    from vispy.scene import visuals
    from vispy import app
    from vispy.util.quaternion import Quaternion
    import sys
    import random
    import math
    import bisect
    import time

    import stocks as s

    import multiprocessing
    from multiprocessing import Process
    def ndEvenDist(ndBounds, count):
        z = np.array([[np.linspace(ndBounds[dim][param][0].astype(np.float64), ndBounds[dim][param][1].astype(np.float64), num=math.ceil(count ** (1 / np.size(ndBounds, axis=0))), endpoint=True, retstep=False, dtype=None, axis=0) for param in range(np.size(ndBounds[dim], axis=0))] for dim in range(np.size(ndBounds, axis=0))])
        z = z.reshape(-1, z.shape[-1])
        meshgrid = np.meshgrid(*z)
        meshgrid = [meshgrid[i].flatten() for i in range(np.size(meshgrid, axis=0))]
        return [meshgrid[a][list(set(np.floor(np.linspace(0, len(meshgrid[a]), num=count + 2, endpoint=True, retstep=False, dtype=None, axis=0)[1:-1]).astype(int)))] for a in range(len(meshgrid))]
    def forecaster(DATA, signalSamples, phaseSamples, binCount):
        DATA = np.array(DATA).astype(np.float64)
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
                binBounds = np.linspace(DATA[0][0] - dimRange, dimRange + DATA[0][-1], binCount+1, endpoint=True)
                bins = [[] for i in range(len(binBounds)-1)]
        sims = ndEvenDist(ndBounds, phaseSamples)
        
        result = {"data":[], "weights":[], "lens":[]}
        simCount = np.size(sims[0])
        startTime = time.perf_counter()

        for s in range(simCount):
            expTimeTaken = (simCount / (s+1)) * (time.perf_counter() - startTime)
            if expTimeTaken > 1 and (s+1) % int(((1/expTimeTaken)*simCount)) == 0:
                print(str(int(((s+1)/simCount)*100)) + "%", str(int(1/expTimeTaken)) + "fps", str(np.round(expTimeTaken - (time.perf_counter() - startTime), 2)) + "s remain")
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
            lenPerc = len(tempDists)/(len(DATA[0]))
            for i in range(len(tempDATA[0])):
                b = bisect.bisect(binBounds, tempDATA[0][i])
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
        result["lens"] = np.array(result["lens"]).astype(np.float64)
        result["weights"] = np.array(result["weights"])
        result["weights"] -= np.amin(result["weights"])
        result["weights"] /= np.amax(result["weights"])
        result["weights"] = ((1-result["weights"]) + result["lens"]) / 2 #1 - (((1 - ((1 - result["weights"]) ** 1)) + (1-result["lens"])) / 2)
        return result
    while True:
        #startTime = time.perf_counter()
        t += 0.1
        #DATA = [np.linspace(0,100, np.size(stockData)), stockData]
        #DATA[0].append(t+0.1)
        #DATA[1].append(np.sin(t))
        A = 20
        DATA = np.array([np.linspace(0+t, 1+t, A), np.array([np.sin(x) + np.cos(x/4) + ((x-t)/1500000) + (random.uniform(0,0) / 10) for x in np.linspace(t,t+12,A)])])
        DATAdim = len(DATA)
        binCount = A * 3
        out = forecaster(DATA, 10, 60, binCount) #signalSamples, phaseSamples, binCount

        weights = np.array([np.full((len(out["data"][0][0])), w) for w in out["weights"]]).flatten()
        colours = []
        for w in weights:
            colours.append([1-w,w/2,w,1-w])
        outData = np.array([np.transpose(out["data"][i]) for i in range(len(out["data"]))])
        outDataShape = np.shape(outData)
        outData = outData.reshape(outDataShape[0] * outDataShape[1], outDataShape[2])
        outData = np.transpose(outData)
        binData = []
        binData.append(out["binLocs"])
        for a in range(DATAdim-1):
            binData.append(out["binned"][a])
        binData = np.array(binData)
        #print("A", len(binData[0]), len(binData[1]), np.transpose(np.array(binData)), "A")
        
        #out = Global.out
        out = {"DATA":DATA, "binData":binData, "colours":colours, "outData":outData, "t":t}
        #print("B", 1 / (time.perf_counter() - startTime))
        Global.out = out
    #Global.alive = False

if __name__ == '__main__':
    from scipy import signal
    from scipy.spatial.transform import Rotation as R
    import numpy as np
    from scipy.interpolate import PchipInterpolator
    import numpy as np
    import vispy
    from vispy import app, visuals, scene
    from vispy.scene import visuals
    from vispy import app
    from vispy.util.quaternion import Quaternion
    import sys
    import random
    import math
    import bisect
    import time

    import stocks as s

    import multiprocessing
    from multiprocessing import Process
    manager = multiprocessing.Manager()
    #global Global
    global processes
    Global = manager.Namespace()
    processes = []
    #############################################
    vispy.use("glfw")

    canvas = vispy.scene.SceneCanvas(keys='interactive', title='Forecaster', show=True)
    canvasTwo = vispy.scene.SceneCanvas(keys='interactive', title='Backtester', show=True)
    view = canvas.central_widget.add_view()
    view.camera = 'fly'
    #############################################
    #This model has no temporal communication, each prediction is independent of every other prediction.
    #1) USE QTHREAD
    #############################################

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

    t = -0.1
    Global.out = {"DATA":[], "binData":[], "colours":[], "outData":[], "t":t}
    #DATA = [[0], [0]]
    #stockData = s.getStockData()[:3000]

    def main():
        print("main: started")
        coreCount = 1#int(multiprocessing.cpu_count() * 0.5)
        processes = []
        for id in range(coreCount):
            p = multiprocessing.Process(target=multiprocessing_func, args=(Global, id, t))
            p.daemon = True
            processes.append(p)
        for core in range(coreCount):
            processes[core].start()
        ###processes[-1].join()

    i = 0
    def update(ev):
        global scatter
        global scatterBase
        global t
        global i
        i += 1
        if t < 0:
            view.camera.center = [0,0,5]
            view.camera.rotation1 = Quaternion.create_from_euler_angles(*[0,0,0], degrees=True)
            view.camera.scale_factor = 1
            #r = R.from_quat([view.camera.rotation.w, view.camera.rotation.x, view.camera.rotation.y, view.camera.rotation.z])
            #print(r.as_euler('zyx', degrees=True))
        if i == 0 or i % 100 == 0:
            DATA = Global.out["DATA"]
            binData = Global.out["binData"]
            colours = Global.out["colours"]
            outData = Global.out["outData"]
            t = Global.out["t"]

            #startTime = time.perf_counter()
            DATA[0] -= np.mean(DATA[0])
            binData[0] -= np.mean(binData[0])
            binData = np.transpose(binData)
            outData[0] -= np.mean(outData[0])
            outData = np.transpose(outData)
            #print("A", 1 / (time.perf_counter() - startTime))
            scatter.set_data(outData[:100000], edge_color=(0,0,1,0), face_color=colours[:100000], size=3)
            #scatterBase.set_data(pos=self.out[0], connect=self.out[1], width=1000, color=(0.5, 0.5, 1, 1))
            scatterBase.set_data(np.transpose(DATA), connect=np.array([[i, i+1] for i in range(len(DATA[0]) - 1)]), color=(1, 1, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=4, face_color=(0.5, 0.5, 1, 0)) #np.zeros(np.size(DATA, 1))
            scatterBinned.set_data(binData, connect=np.array([[i, i+1] for i in range(len(binData) - 1)]), color=(0.5, 0.5, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=2, face_color=(0.5, 0.5, 1, 0))

    timer = app.Timer()
    timer.connect(update)
    timer.start(0)
    if sys.flags.interactive == 0:
        main()
        canvas.show()
        app.run()