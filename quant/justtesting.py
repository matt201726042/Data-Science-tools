import numpy as np

def acorr(signal):
    out = np.array([])
    dims = len(signal)
    out = np.array(([[np.mean(np.abs(signal[d][:-i] - signal[d][i:])) for i in range(1,len(signal[d]))] for d in range(dims)]))
    return np.sum(out**2,axis=0)**(1/2)

print(acorr(np.array([[1,2,3],[1,2,3],[1,2,3]])))