#!/usr/bin/env python

from flask import Flask, request
from threading import Thread, RLock, Event, Timer
from multiprocessing import Process
from signal import signal, SIGINT
import sys
import cv2
import numpy as np

#======================================================================

class Globals(object):
    def __init__(self):
        self.camLock = RLock()
        self.frameLock = RLock()
        self.captureEvent = Event()

G = Globals()

#======================================================================

class Webcam(object):
    def __init__(self):
        self.frameW = 640
        self.frameH = 480

        self.stop = False

        self.cvFrame = np.zeros((self.frameH, self.frameW, 3), np.uint8)
        self.cvFrameN = 1

        self.cam = None
        self.camThread = Thread()

    def cvloop(self):
        while True:
            print "p",
            if G.dbg_lock: print "cvloop wait camLock... ",
            with G.camLock:
                if G.dbg_lock: print "using lock"
                ret, f = G.cam.read()
            if W.stop: break
            if G.dbg_lock: print "cvloop wait frameLock... ",
            with G.frameLock:
                if G.dbg_lock: print "using lock"
                self.cvFrame = f
                self.cvFrameN += 1
            G.captureEvent.wait()
            if W.stop: break
        print "camera shutdown"
        G.cam.release()

W = Webcam()


#======================================================================

class FlaskServer(Process):
    def __init__(self):
        self.app = Flask(__name__)
        self.server = Process(target=self.app.run,kwargs={'host':'0.0.0.0'})

    def shutdown_server(self):
        shutdown = request.environ.get('werkzeug.server.shutdown')
        if shutdown is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        shutdown()

F = FlaskServer()

#======================================================================

@F.app.route('/')
def hello_world():
    return 'Hello World!'

def sigint_handler(signum, frame):
    print "Keyboard or Signal interrupt"
    F.server.terminate()

#======================================================================

if __name__ == '__main__':

    # Webcam
    W.cam = cv2.VideoCapture(0)
    W.camThread.target=W.cvloop
    W.camThread.start()

    # Bindings
    signal(SIGINT, sigint_handler)

    # Flask server
    F.server.start()
    F.server.join()

    # Cleanup
    W.stop = True
    G.captureEvent.set()
    W.camThread.join()
    cv2.destroyAllWindows()
