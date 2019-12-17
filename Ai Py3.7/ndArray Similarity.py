import numpy as np
import scipy
from scipy import spatial
from scipy.spatial import distance
import time
import random

#Code to calculate 'differences' between n dimensional scatter graphs.
#There will always be a 'base', defined as A, and then 'others' which are compared with A. There are 5 others - consisting of 10 coordinates and 3 dimensions.

A = np.array([[random.uniform(0,10) for i in range(2)] for i in range(5)])
others = np.array([[[random.uniform(0,10) for a in range(2)] for b in range(5)] for c in range(400)])

startTime = time.perf_counter()
differences = np.array([np.mean([np.mean([distance.euclidean(A[point], others[which][otherPoint]) for otherPoint in range(np.size(others[which], axis=0))]) for point in range(np.size(A, axis=0))]) for which in range(np.size(others,axis=0))])
print("differences", differences)
print("time taken", time.perf_counter() - startTime)
print("fps", 1 / (time.perf_counter() - startTime))