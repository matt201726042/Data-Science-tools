#import scipy
#from scipy import ndimage
import numpy as np
import math
import numpy as np
import itertools
import time
from scipy import optimize
from scipy.spatial import distance
import sys

import vispy
import vispy.scene
from vispy.scene import visuals
from vispy import app

import sys
import OpenGL.GL as gl

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtOpenGL import QGLWidget


class MyQGLWidget(QGLWidget):
    init = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def glInit(self):
        super().glInit()
        self.init.emit()

    def gl_gen_lists(self, size):
        return gl.glGenLists(size)


class App(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.qgl_widget = MyQGLWidget()
        self.qgl_widget.init.connect(self.on_init)
        self.qgl_widget.show()

    def on_init(self):
        self.qgl_widget.makeCurrent()
        print(self.qgl_widget.gl_gen_lists(1))

np.set_printoptions(precision=10)
np.set_printoptions(suppress=True)

canvas = vispy.scene.SceneCanvas(keys='interactive', show=True)
view = canvas.central_widget.add_view()
view.camera = 'turntable'
scatter = visuals.Markers()
view.add(scatter)
axis = visuals.XYZAxis(parent=view.scene)

def sinwave(rang):
    return np.sin(rang)

def f(k):
    return k

t=0
def update(ev):
    global t
    global scatter
    t += 1
    rang = np.linspace(t,t+360,1000)
    result = f(sinwave(rang))
    x,y = rang,result
    scatter.set_data(np.transpose([x,y]), edge_color=None, face_color=(0, 0, 1, 1), size=5)

timer = app.Timer()
timer.connect(update)
timer.start(0.001)
if __name__ == '__main__':
    canvas.show()
    if sys.flags.interactive == 0:
        app.run()