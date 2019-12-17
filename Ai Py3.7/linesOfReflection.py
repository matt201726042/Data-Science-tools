import numpy as np
import itertools

DATA = np.array([[1,2,3], [1,2,3]])

mins = [np.amin(DATA[i]) for i in range(np.size(DATA, axis=0))]
maxes = [np.amax(DATA[i]) for i in range(np.size(DATA, axis=0))]
points = list(itertools.product(*zip(mins,maxes))) #corners

from itertools import combinations
import time
lines = [((x1, y1), (x2, y2)) for (x1, y1), (x2, y2) in combinations(points, 2) if x1 == x2 or y1 == y2]
print(lines)