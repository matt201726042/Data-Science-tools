import numpy as np
import vispy
import vispy.scene
from vispy.scene import visuals
from vispy import app
import sys

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

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
view.camera = 'turntable'
# generate data
def solver(t):
    pos = np.array([[np.sin(t * i) * np.sin(i) * 4, np.cos(t * i - t) * np.sin(i + t) * 4,np.sin(i * t) * np.cos(i)] for i in range(1, 5000)])
    return pos

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

    DATA = np.array([[x for x in range(20)], [0 for y in range(20)]])

    perf = [[], []]
    resultParity = np.array([]) #Similarities
    z = int(z)
    for i in range(z, z+1, 1): #Nearing ##math.ceil(count ** (1 / np.size(ndBounds[dim], axis=0)))## may cause weird distribution

        #ax1.clear()
        #ax3.clear()
        #ax3.scatter(*DATA, color='blue', s=10 ** 2)
        count = i#((np.sin(i / 5) + 2) * 10).astype(int)
        #perf[0].append(count)
        #startTime = time.time_ns() / (10 ** 9)

        ndBounds = np.zeros(shape=(np.size(DATA, axis=0),3,2))
        dimRangeMult = 1
        for dim in range(np.size(DATA, axis=0)):
            dimRange = np.amax(DATA[dim]) - np.amin(DATA[dim])
            lowerBound = np.amin(DATA[dim]) - (1 * dimRange)
            upperBound = np.amax(DATA[dim]) + (1 * dimRange)
            #ndBounds[dim] = np.array([[1,1], [lowerBound, upperBound], [-dimRange, dimRange]]) #scale factor, scale center, phase             #doubleRefl center???, ["rotate", 0, 360 - ((360 - 0) / (count + 1))]
            ndBounds[dim] = np.array([[-dimRange, dimRange]])
            dimRangeMult += dimRange

        result = ndEvenDist(ndBounds, count, resultParity)

        params = 2
        resultDimensions = np.size(result, axis=0)
        dimensions = np.size(DATA, axis=0)
        toReturn = []
        for task in range(np.size(result[0], axis=0)):
            #startTimeTwo = time.perf_counter()
            tempDATA = DATA
            overlapIndexes = []
            for dim in range(resultDimensions // params): # amount of parameters (dimensions) passed into ndEvenDist
                offset = params * dim
                temp = scale(DATA[dim], result[offset][task], result[offset + 1][task])
                #temp = phase(temp, result[offset + 2][task])
                tempDATA[dim] = temp
                overlapIndexes.append(np.where((np.amin(DATA[dim]) <= temp) & (temp <= np.amax(DATA[dim])))[0])
            validOverlaps = commonElements(overlapIndexes)
            if np.size(validOverlaps, axis=0) > 0:
                validForComparison = [[[tempDATA[dim][i] for i in validOverlaps] for dim in range(dimensions)]]
                similarity = ndSimilarity(np.array(DATA), validForComparison, dimRangeMult)
                resultParity = np.append(resultParity, similarity)
                #print("task", task, ":", 1 / (time.perf_counter() - startTimeTwo), "fps", similarity, "similarity")
                #colormap = plt.cm.get_cmap('Purples')
                toReturn.append([[tempDATA[dim][i] for dim in range(np.size(tempDATA, axis=0))] for i in range(np.size(tempDATA[dim]))])
        return toReturn


# These are the data that need to be updated each frame --^

scatter = visuals.Markers()
view.add(scatter)


#view.camera = scene.TurntableCamera(up='z')

# just makes the axes
axis = visuals.XYZAxis(parent=view.scene)


t = 1
def update(ev):
    global scatter
    global t
    t += 1
    try:
        result = np.array(body(t))
        result = result.reshape(-1, result.shape[-1])
        scatter.set_data(result, edge_color=None, face_color=(0, 0, 1, 1), size=10)
    except:
        pass

timer = app.Timer()
timer.connect(update)
timer.start(0)
if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()