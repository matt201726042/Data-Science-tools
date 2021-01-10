import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from dateutil.rrule import rrule, MONTHLY
import matplotlib.patches as patches
from dateutil.relativedelta import relativedelta

lines=[]

#of running python script
dirname, filename = os.path.split(os.path.abspath(__file__))

directory = dirname + "\data"

for root,dirs,files in os.walk(directory):
    for file in files:
        if file.endswith(".csv"):
            print(directory + "\\" + file)
            f=open(directory + "\\" + file, 'r')
            for line in f:
                lines.append(line)
            f.close()

fieldNames = lines[0][:-1].split(",")[1:-1]

del lines[0]

datapoints = []
lines = lines[::-1]
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

def kernelRollingAverage(datapointsT, kernel=[[-604800,0,604800], [0,1,0]]): #datapointsT should already be filtered for None's
    d = datapointsT
    out = []
    termNum = (d[0][-1] - d[0][0]) / max(kernel[0])
    pointsPerTerm = round(len(d[0]) / termNum)
    
    for p in range(len(d[0])):
        window = [[], []]
        timeDisps = []
        for otherP in range(len(d[0])): #moving through the kernel window
            timeDisp = (d[0][otherP] - d[0][p])
            timeDisps.append(timeDisp)
    
        for n in range(len(timeDisps)):
            if n > 0:
                if timeDisps[n-1] <= 0 and timeDisps[n] >= 0:
                    middleIndex = n
        
        win = [x for _,x in sorted(zip(np.abs(timeDisps),[p for p in range(len(timeDisps))]))][:pointsPerTerm-1]
        winMult = np.abs(timeDisps[win[-1]]) / np.max(kernel[0])
        for otherP in [x for _,x in sorted(zip(np.abs(timeDisps),[p for p in range(len(d[0]))]))][:pointsPerTerm-1]:
            window[0].append(d[1][otherP]) #append the value to the window
            window[1].append(np.interp([timeDisps[otherP]], np.array(kernel[0]) * winMult, kernel[1])[0]) #append the weight to the window
        out.append(np.average(window[0], weights=window[1]))
    return out

def drawMonths():
    rang = [datapointsT[0][0], datapointsT[0][-1]]

    strt_dt = datetime.fromtimestamp(rang[0])
    end_dt = datetime.fromtimestamp(rang[1])

    dates = [dt for dt in rrule(MONTHLY, dtstart=strt_dt, until=end_dt)]
    dates.append(dates[-1] + relativedelta(months=1))
    mTs = []
    for month in dates:
        month = month.replace(day=1)
        month = month.replace(hour=0)
        month = month.replace(minute=0)
        month = month.replace(second=0)
        mTs.append(month.timestamp())
    for pair in range(len(mTs) - 1):
        pairPerc = (pair) / len(mTs)
        rect = patches.Rectangle((mTs[pair],0),mTs[pair+1]-mTs[pair],1,linewidth=1,facecolor=(0,pairPerc,1-pairPerc,0.15))
        ax.add_patch(rect)
        plt.text((mTs[pair] + mTs[pair+1]) / 2, 0, dates[pair].strftime('%B'), fontsize=12, horizontalalignment='center')
    pairPerc = 1
    rect = patches.Rectangle((mTs[-1],0),rang[1]-mTs[-1],1,linewidth=1,facecolor=(0,pairPerc,1-pairPerc,0.15))
    ax.add_patch(rect)

fig,ax = plt.subplots(1)

allOnTheSameGraph = True
term = 604800 * 4 #in seconds, for moving average

if allOnTheSameGraph:
    rang = 1
else:
    rang = 100000000000000000
for i in range(rang):
    if allOnTheSameGraph:
        drawMonths()
    for fieldNum in range(len(fieldNames)):
        #if not allOnTheSameGraph:
            #fig.clf() #if you remove this, make sure to normalise.
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

        y = kernelRollingAverage([x,y], [[-term,0,term], [0,1,0]])

        plt.plot(x, y, linewidth=0.75, alpha=1, label=fieldNames[fieldNum])
        plt.legend()
        if not allOnTheSameGraph:
            drawMonths()
            plt.show()
        else:
            plt.draw()
            plt.legend()
            plt.pause(0.000000001)
plt.pause(100)