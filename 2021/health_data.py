import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

lines=[]

#of running python script
dirname, filename = os.path.split(os.path.abspath(__file__))

directory = dirname + "\data"
print(directory)

for root,dirs,files in os.walk(directory):
    for file in files:
        if file.endswith(".csv"):
            f=open(directory + "\\" + file, 'r')
            for line in f:
                lines.append(line)
            f.close()

fieldNames = lines[0][:-1].split(",")[1:-1]

del lines[0]

datapoints = []
for line in lines:
    splitLine = line.split(",")
    timestamp = "".join(splitLine[:2])[1:-1]
    dt_object = datetime.strptime(timestamp, "%b %d %Y %I:%M:%S %p")
    dt_object_seconds = dt_object.timestamp()
    fields = []
    for field in splitLine[2:-1]:
        try:
            fields.append(float(field))
        except:
            fields.append(None)
    datapoints.append([dt_object_seconds, *fields])

datapointsT = np.transpose(datapoints)
print(datapointsT)
print(fieldNames)
fieldNum = 2
x = datapointsT[0]
y = datapointsT[1+fieldNum]

def kernelRollingAverage(datapointsT, kernel=[[-604800,0,604800], [0,1,0]]): #datapointsT should already be filtered for None's
    d = datapointsT
    out = []
    for p in range(len(d[0])):
        window = [[], []]
        for otherP in range(len(d[0])): #moving through the kernel window
            timeDisp = (d[0][otherP] - d[0][p])
            if kernel[0][0] <= timeDisp <= kernel[0][-1]:
                window[0].append(d[1][otherP]) #append the value to the window
                window[1].append(np.interp([timeDisp], kernel[0], kernel[1])[0]) #append the weight to the window
        out.append(np.average(window[0], weights=window[1]))
    return out



allOnTheSameGraph = False
if allOnTheSameGraph:
    rang = 1
else:
    rang = 100000000000000000
for i in range(rang):
    for fieldNum in range(len(fieldNames)):
        if not allOnTheSameGraph:
            plt.clf() #if you remove this, make sure to normalise.
        tempX = list(datapointsT[0])
        tempY = datapointsT[1+fieldNum]
        noneIndexes = []
        for p in range(len(datapointsT[0])):
            if datapointsT[1+fieldNum][p] == None:
                noneIndexes.append(p)
        for index in sorted(noneIndexes, reverse=True):
            del tempX[index]
        x = tempX
        tempY = tempY[tempY != np.array(None)]
        if not allOnTheSameGraph:
            y = tempY
        else:
            y = (tempY - np.amin(tempY)) / (np.amax(tempY) - np.amin(tempY)) #normalised?

        y = kernelRollingAverage([x,y])

        plt.plot(x, y, linewidth=0.75, alpha=1, label=fieldNames[fieldNum])
        plt.legend()
        if not allOnTheSameGraph:
            plt.show()
        else:
            plt.draw()
            plt.pause(0.000000001)
plt.pause(100000000000)