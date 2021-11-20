from re import T
import numpy as np
import time
from scipy import signal

import vispy
from vispy import app, visuals, scene
from vispy.scene import visuals
from vispy import app
from vispy.util.quaternion import Quaternion
import sys

import stocks as s

#############################################
vispy.use("glfw")
canvas = vispy.scene.SceneCanvas(keys='interactive', title='Forecaster', show=True)
canvasTwo = vispy.scene.SceneCanvas(keys='interactive', title='Backtester', show=True)
view = canvas.central_widget.add_view()
view.camera = 'fly'
#############################################
#This model has no temporal communication, each prediction is independent of every other prediction.
#1) USE QTHREAD
#2) Note that if the input time dimension is not regularly distributed, the bin graph will draw out of place under the assumption of a regular distribution for optimisation purposes
#############################################
Plot3D = scene.visuals.create_visual_node(vispy.visuals.line_plot.LinePlotVisual)
scatter = visuals.Markers()
view.add(scatter)
scatterBase = Plot3D()
view.add(scatterBase)
scatterBinned = Plot3D()
view.add(scatterBinned)
scatterDiff = Plot3D()
view.add(scatterDiff)
scatterProfit = Plot3D()
view.add(scatterProfit)
#view.camera = scene.TurntableCamera(up='z')
axis = visuals.XYZAxis(parent=view.scene)

if __name__ == "__main__":
    class ExchangeUser: #Slippage is not modelled, bitfinex fees are
        def __init__(self, balance):
            self.balance = balance
            self.holding = 0 #in terms of volume
            self.positions = []
            self.fees = 0
            print("BALANCE", self.balance, "HOLDING", self.holding)
        def getPortfolioValue(self, price):
            return self.balance + (self.holding * price) - self.fees
        def getHolding(self):
            return self.holding
        def getBalance(self):
            return self.balance
        def order(self, direction, volume, price): #direction 1 is LONG, direction -1 is SHORT
            #print("DIRECTION", direction, "VOLUME", volume, "PRICE", price, "BALANCE", self.balance, "HOLDING", self.holding)
            if self.balance >= 0:
                if direction > 0 and (volume * price) <= self.balance:
                    self.holding += volume
                    self.balance -= volume * price
                    self.fees += volume * price * 0.002
                elif direction < 0 and (volume * price) <= self.balance + (self.holding * price):
                    self.holding -= volume
                    self.balance += volume * price
                    self.fees += volume * price * 0.002
                else:
                    print("FAIL")
                    return False #FAIL
                return True
            else:
                pass
                #self.balance = -0.0001
                #self.fees = 0
                #self.holding = 0
        def getMaxOrderVol(self, price):
            return self.balance / price

    def acorr(signal):
        out = np.array([])
        dims = len(signal)
        out = np.array(([[np.mean(np.abs(signal[d][:-i] - signal[d][i:])) * i for i in range(1,len(signal[d]))] for d in range(dims)]))
        return np.sum(out**2,axis=0)**(1/2)

    global t
    t = 2
    stockData = s.getStockData()
    stockData = [np.arange(len(stockData["Close"])), stockData["Close"], stockData["Volume"], stockData["High"] - stockData["Low"]]
    stockData = np.transpose(np.transpose(stockData)[::int(np.ceil(len(stockData)/20000000))])

    preds = []
    profits = []
    user = ExchangeUser(stockData[1][0])
    def update(ev):
        global t
        t += 1
        if t >= len(stockData[0]):
            timer.stop()
        #length = 100
        length = t
        #x = np.arange(length)
        x = stockData[0][:t]
        #a = np.sin((x+t)/50) + np.cos((x-t)/200)
        a = stockData[1][:t]
        y = np.diff(a)
        y2 = np.diff(stockData[2][:t])
        y3 = np.diff(stockData[3][:t])

        a1 = acorr([y,y2,y3])
        a1 = np.concatenate([[0],(1-((a1 - np.amin(a1)) / (np.amax(a1) - np.amin(a1)))) ** 100])
        out = signal.convolve(y,a1) / signal.convolve(a1,np.ones(length-1))
        out = np.concatenate([[a[-1]], out[length-1:]])
        out = np.cumsum(out)

        scaleX = 1/np.amax(x)
        scaleY = 1/np.amax(a)
        preds.append((out[1] / out[0]))
        #preds.append(stockData[1][t] / stockData[1][t-1])
        if len(preds) > 2 and np.sign(preds[-1] - 1) != np.sign(preds[-2] - 1):
            user.order(-np.sign(user.getHolding()), np.abs(user.getHolding()), a[-1])
        if (len(preds) > 2 and np.sign(preds[-1] - 1) != np.sign(preds[-2] - 1)) or len(preds) > 1:
            profits.append(user.getPortfolioValue(a[-1]))
            if preds[-1] > 1:
                user.order(1,user.getMaxOrderVol(a[-1]),a[-1])
            elif preds[-1] < 1:
                user.order(-1,user.getMaxOrderVol(a[-1]),a[-1])
            print("DAY", t, "RETURNS ON INITIAL PER YEAR", ((profits[-1]/a[0]) ** (1/(t/365)) - 1) * 100, "%")
            scatterProfit.set_data(np.transpose([x[3:]*scaleX, np.array(profits)*scaleY]), color=(0.5, 1, 0.5, 1), edge_color=(0.5, 1, 0.5, 0), width=3, face_color=(0.5, 0.5, 1, 0))
        #sfs = input()
        scatterBase.set_data(np.transpose([x*scaleX,a*scaleY]), color=(1, 1, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=3, face_color=(0.5, 0.5, 1, 0))
        scatterBinned.set_data(np.transpose([(x[1:]+(length-2))*scaleX,out*scaleY]), connect=np.array([[i, i+1] for i in range(length-2)]), color=(0.5, 0.5, 1, 1), edge_color=(0.5, 0.5, 1, 0), width=2, face_color=(0.5, 0.5, 1, 0))
        scatterDiff.set_data(np.transpose([x[1:]*scaleX,a1]),connect=np.array([[i, i+1] for i in range(length-2)]), color=(1, 0.5, 0.5, 1), edge_color=(1, 0.5, 0.5, 0), width=2, face_color=(1, 0.5, 0.5, 0))
    timer = app.Timer()
    timer.connect(update)
    timer.start(0)
    if sys.flags.interactive == 0:
        canvas.show()
        app.run()