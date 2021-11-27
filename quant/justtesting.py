import numpy as np

p = []
for i in range(10):
    a = np.ma.empty(((i*2)+1))
    a.mask = True
    a[-(i+1):] = np.arange(i+1) #+i
    p.append(a)

def lagMean(p):
    lenp = len(p)
    arr = np.ma.empty((lenp,len(p[-1])))
    arr.mask = True
    for i in range(lenp):
        arr[i,:len(p[i])] = p[i]
    return np.ma.average(arr, axis=0, weights=np.geomspace(1,1000000000000,num=lenp))[lenp:]

#print(lagMean(p))
print([1,2,3][:2])