import numpy as np

sMapValues = np.array([[1,2,3,2,1], [1,2,3,2,1]])
sMapLocats = np.array([[-2,-1,0,1,2], [-2,-1,0,1,2]])

sMapTEMPValues = sMapValues
for dimension in range(2):
    sMapTEMPValues[dimension] = np.amax(sMapTEMPValues[dimension]) - sMapTEMPValues[dimension]
print(np.cumsum(sMapTEMPValues, axis=1))