#import scipy
#from scipy import ndimage
import numpy as np
import math
import numpy as np
import itertools
import time
from scipy import optimize
from scipy.spatial import distance
import sys

import vispy
import vispy.scene
from vispy.scene import visuals
from vispy import app

np.set_printoptions(precision=10)
np.set_printoptions(suppress=True)


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
view.camera = 'turntable'
scatter = visuals.Markers()
view.add(scatter)
axis = visuals.XYZAxis(parent=view.scene)


def ndEvenDist(ndBounds, count, resultParity):
    z = np.array([[np.linspace(ndBounds[dim][param][0].astype(np.float), ndBounds[dim][param][1].astype(np.float), num=math.ceil(count ** (1 / np.size(ndBounds[dim], axis=0))), endpoint=True, retstep=False, dtype=None, axis=0) for param in range(np.size(ndBounds[dim], axis=0))] for dim in range(np.size(ndBounds, axis=0))])
    z = z.reshape(-1, z.shape[-1])
    meshgrid = np.meshgrid(*z)
    meshgrid = [meshgrid[i].flatten() for i in range(np.size(meshgrid, axis=0))]
    return [meshgrid[a][list(set(np.floor(np.linspace(0, len(meshgrid[a]), num=count + 2, endpoint=True, retstep=False, dtype=None, axis=0)[1:-1]).astype(int)))] for a in range(len(meshgrid))]


def ndSimilarity(base, others, dimRangeMult):
    diffs = np.array([])
    for which in range(np.size(others, axis=0)):
        for dim in range(np.size(base, axis=0)):
            for point in range(np.size(others[which][dim], axis=0)):
                for otherPoint in range(np.size(others[which][dim], axis=0)):
                    diffs = np.append(diffs, distance.euclidean(base[dim][point], others[which][dim][otherPoint]))
    return np.mean(diffs) / dimRangeMult


def commonElements(arr):
    result = set(arr[0])
    for currSet in arr[1:]:
        result.intersection_update(currSet)
    return list(result)


def phase(origin, dimPhase):
    # origin must be a numpy array
    result = origin.astype(float) + dimPhase.astype(float)
    return result


def scale(origin, factor, center):
    # origin must be a numpy array
    result = (((origin - center) * factor) + center)
    return result


def doubleRefl(points, AA, AB, BA, BB):
    A_vector = AB - AA
    B_vector = BA - BB
    A_hat = A_vector / (A_vector ** 2).sum() ** 0.5
    B_hat = B_vector / (B_vector ** 2).sum() ** 0.5
    result = np.array([])
    for i in range(np.size(points, 0)):
        point_refl = -points[i] + 2 * AA + 2 * A_hat * np.dot((points[i] - AA), A_hat)
        point_doubleRefl = -point_refl + 2 * BA + 2 * B_hat * np.dot((point_refl - BA), B_hat)
        result = np.vstack((*[result[i] for i in range(len(result))], point_doubleRefl))
    return result

def body(z):
    global scatter

    #figure = plt.figure() #gcf()
    #figureTwo = plt.figure()
    #ax1 = Axes3D(figure) #figure.add_subplot(111, projection='3d')
    #ax2 = Axes3D(figureTwo)

    DATA = np.array([[x for x in range(10)], [np.sin(y / 5) for y in range(10)], [np.sin(z / 5) for z in range(10)]])
    #print(DATA)

    #if np.size(DATA, axis=0) > 2:
        #figureThree = plt.figure()
        #ax3 = Axes3D(figureThree)  # figure.add_subplot(111)
    #else:
        #figureThree = plt.figure()
        #ax3 = figureThree.add_subplot(111)

    # Scaling # Computational plausibility put on the line.
    # Displacement
    # Rotation

    perf = [[], []]
    resultParity = np.array([])
    print(z)
    for i in range(z, z+1, 1): #Nearing ##math.ceil(count ** (1 / np.size(ndBounds[dim], axis=0)))## may cause weird distribution

        #ax1.clear()
        #ax3.clear()
        #ax3.scatter(*DATA, color='blue', s=10 ** 2)
        count = i#((np.sin(i / 5) + 2) * 10).astype(int)
        perf[0].append(count)
        startTime = time.time_ns() / (10 ** 9)

        ndBounds = np.zeros(shape=(np.size(DATA, axis=0),3,2))
        dimRangeMult = 1
        for dim in range(np.size(DATA, axis=0)):
            dimRange = np.amax(DATA[dim]) - np.amin(DATA[dim])
            lowerBound = np.amin(DATA[dim]) - (1 * dimRange)
            upperBound = np.amax(DATA[dim]) + (1 * dimRange)
            ndBounds[dim] = np.array([[0.25,4], [lowerBound, upperBound], [-dimRange, dimRange]]) #scale factor, scale center, phase             #doubleRefl center???, ["rotate", 0, 360 - ((360 - 0) / (count + 1))]
            dimRangeMult += dimRange

        result = ndEvenDist(ndBounds, count, resultParity)

        params = 3
        resultDimensions = np.size(result, axis=0)
        dimensions = np.size(DATA, axis=0)
        result = []
        for task in range(np.size(result[0], axis=0)):
            startTimeTwo = time.perf_counter()
            tempDATA = np.array([[x for x in range(10)], [np.sin(y / 5) for y in range(10)], [np.sin(z / 5) for z in range(10)]])
            overlapIndexes = []
            for dim in range(resultDimensions // params): # amount of parameters (dimensions) passed into ndEvenDist
                offset = params * dim
                temp = scale(DATA[dim], result[offset][task], result[offset + 1][task])
                temp = phase(temp, result[offset + 2][task])
                tempDATA[dim] = temp
                overlapIndexes.append(np.where((np.amin(DATA[dim]) <= temp) & (temp <= np.amax(DATA[dim])))[0])
            validOverlaps = commonElements(overlapIndexes)
            if np.size(validOverlaps, axis=0) > 0:
                validForComparison = [[[tempDATA[dim][i] for i in validOverlaps] for dim in range(dimensions)]]
                similarity = ndSimilarity(np.array(DATA), validForComparison, dimRangeMult)
                resultParity = np.append(resultParity, similarity)
                print("task", task, ":", 1 / (time.perf_counter() - startTimeTwo), "fps", similarity, "similarity")
                #colormap = plt.cm.get_cmap('Purples')
                result.append([[tempDATA[dim][i] for dim in range(np.size(tempDATA, axis=0))] for i in range(np.size(tempDATA[dim]))])
                #scatter.set_data([[tempDATA[dim][i] for dim in range(np.size(tempDATA, axis=0))] for i in range(np.size(tempDATA[dim]))], edge_color=None, face_color=(1, 1, 1, 1), size=5)
                #ax3.scatter(*tempDATA, color=colormap((similarity / 0.25) ** 6), alpha=(0.1), s=((similarity / 0.25) ** 6)) #, [similarity for a in range(np.size(tempDATA[0], axis=0))]
                #ax1.scatter(result[0][task], result[1][task])
                #plt.draw()
                #plt.pause(0.0000000001)
        return result







        #sampleOutput = np.array([])
        #for inputDim in range(len(result) // 4):
            #for transf in range(len(result[0])):
                #for part in range(len(result)):
                    #if part == 0:
                        #temp = scale(sampleInput[inputDim], result[part][transf], result[part + 1][transf])
                    #if part == 2:
                        #temp = phase(temp, result[part][transf])
                #if sampleOutput.size < 1:
                    #sampleOutput = np.vstack([temp])
                #else:
                    #sampleOutput = np.vstack(([sampleOutput[i] for i in range(len(sampleOutput))], [temp]))
            #print(sampleOutput)

        perf[1].append((time.time_ns() / (10 ** 9)) - startTime)
        #ax2.clear()
        #ax2.plot(np.array(perf[0]), perf[1])

        #if len(perf[0]) > 2:
            #def test_func(x, a, b, c):
                #return (a * (x ** 2)) + (b * x) + c
            #params = optimize.curve_fit(test_func, perf[0], perf[1])[0]
            #x = np.linspace(min(perf[0]), max(perf[0]) * 2,100)
            #y = test_func(x, params[0], params[1], params[2])
            #ax2.plot(x, y, label='{}'.format([i, params]))
            #ax2.legend

t = 0
def update(ev):
    global t
    global scatter
    t += 1
    result = body(t)
    for i in range(result):
        scatter.set_data(result, edge_color=None, face_color=(0, 0, 1, 1), size=5)

timer = app.Timer()
timer.connect(body)
timer.start(0)
if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()