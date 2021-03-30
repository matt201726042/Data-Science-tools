import scipy.interpolate
import numpy as np
import lda
import random

LOG = [{"content":"Hello"}, {"content":"Goodbye"}, {"content":"Hello"}]

contextWProf = [1,0] #Weight profile
contextLen = 10
contextWProfInterp = scipy.interpolate.PchipInterpolator(np.linspace(0,contextLen-1, num=len(contextWProf)), contextWProf)

reptWProf = [100,0]
reptWTime = [0, 60*60] #seconds
reptCap = 20
reptWProfInterp = scipy.interpolate.PchipInterpolator([0, 60*60], [1,0])

realContext = LOG[-contextLen:]
y = []
LOGlen = len(LOG) - 1
sims = [[] for i in range(LOGlen)]
y = []
for i in range(0, len(LOG)-1):
    if i % 40 == 0:
        print(100 * (i/LOGlen), "%")
    a = lda.LDAquery(LDAMODEL, LDADICT, [c["content"] for c in LOG[:i]], LOG[i+1]["content"])
    for j in range(len(a)):
        sims[j].append(a[j])
for i in range(0, len(LOG)-1):
    sims[i] = sims[i][-10:]
    msg = LOG[LOGlen-i]["content"]
    weights = contextWProfInterp([k for k in range(len(sims[i])-1, -1, -1)])
    rW = reptWeighter(msg)
    y.append((np.average(sims[i], weights=weights) / rW, msg))
print(y)