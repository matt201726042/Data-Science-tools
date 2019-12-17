from scipy import signal
import numpy as np
from scipy.interpolate import PchipInterpolator
import numpy as np
import vispy
import vispy.scene
from vispy.scene import visuals
from vispy import app
import sys

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
view.camera = 'turntable'
# generate data

def weightedAvgConvolve(first, second):
    convOne = signal.convolve(first, second)
    convTwo = signal.convolve([1 for i in range(len(first))], second)
    return convOne, convTwo  # np.divide(convOne, convTwo) #

def autocorr(x):
    diffs = np.array([])
    for lag in range(x.size - 1):
        diffs = np.append(diffs, (1 / (np.mean(np.absolute(x[:x.size - lag - 1] - x[lag + 1:])) + 1) ** 2))
    diffs = np.insert(diffs, 0, 1)
    diffs = np.insert(diffs, 0, diffs[1:][::-1])
    return diffs

def predictor(DATA, samples):

    x = np.linspace(tempDATA[0][0] - span, tempDATA[0][-1] + span, predictLen) - span
    y = rowsSum / np.sum(divisors, axis=0)
    z = [0 for x in range(predictLen)]
    return np.array([[x[i], y[i], z[i]] for i in range(x.size)])
# These are the data that need to be updated each frame --^

scatter = visuals.Markers()
view.add(scatter)

#view.camera = scene.TurntableCamera(up='z')

# just makes the axes
axis = visuals.XYZAxis(parent=view.scene)

t = 0
def update(ev):
    global scatter
    global t
    t += 1
    DATA = [np.linspace(1, 2, 360), np.array([np.sin(x / 1) for x in range(t, t+360)])]
    #DATA = [[1,2,3], [1,2,3]]
    scatter.set_data(predictor(DATA, 100), edge_color=None, face_color=(1, 1, 1, .5), size=5)

timer = app.Timer()
timer.connect(update)
timer.start(0)
if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()