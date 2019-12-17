import numpy as np
import scipy.interpolate

def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[result.size//2:]


from numpy import *


def estimated_autocorrelation(x):
    """
    http://stackoverflow.com/q/14297012/190597
    http://en.wikipedia.org/wiki/Autocorrelation#Estimation
    """
    n = len(x)
    variance = x.var()
    x = x - x.mean()
    r = correlate(x, x, mode='full')[-n:]
    assert allclose(r, array([(x[:n - k] * x[-(n - k):]).sum() for k in range(n)]))
    result = r / (variance * (arange(n, 0, -1)))
    return result


DATA = np.array([[1,2,3], [1,2,3]])
tempDATA = np.zeros((2, 10))
for dim in range(2):
    pchip = scipy.interpolate.PchipInterpolator(DATA[dim], DATA[1 - dim])
    tempDATA[dim] = pchip(np.linspace(np.amin(DATA[dim]), np.amax(DATA[dim]), num=10))
    print(np.convolve(tempDATA[dim], estimated_autocorrelation(tempDATA[dim])))