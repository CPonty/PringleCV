#!/usr/bin/env python

from flask import Flask, request
from threading import Thread, RLock, Event, Timer
from multiprocessing import Process
from signal import signal, SIGINT
import sys
import cv2
import numpy as np

#======================================================================

class Globals(object): pass
G = Globals()

G.cam = None
G.camThread = None

G.camLock = RLock()
G.frameLock = RLock()

G.captureEvent = Event()

G.dbg_lock = False

#======================================================================

class FlaskServer(object): pass
F = FlaskServer()

F.app = Flask(__name__)
F.server = Process(target=F.app.run, args=('0.0.0.0',)) #host='0.0.0.0'

#======================================================================

class Webcam(object):
    frameW = 640
    frameH = 480
    cvFrame = np.zeros((frameH, frameW, 3), np.uint8)
    cvFrameN = 1
    stop = False

    def cvloop(self):
        while True:
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

@F.app.route('/')
def hello_world():
    return 'Hello World!'

#def run_server(): pass
#    F.app.run(host='0.0.0.0')

def stop():
    print "STOP."
    W.stop = True
    G.captureEvent.set()  #allows the capture thread to unblock if paused
    print "1"; sys.stdout.flush()
    G.camThread.join()
    print "2"; sys.stdout.flush()
    cv2.destroyAllWindows()
    print "3"; sys.stdout.flush()
    F.server.terminate()
    print "4"; sys.stdout.flush()
    F.server.join()

def shutdown_server():
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    shutdown()
    stop()

def sigint_handler(signum, frame):
    print "Keyboard or Signal interrupt"
    stop()

#======================================================================

if __name__ == '__main__':

    # Bindings
    signal(SIGINT, sigint_handler)

    # Camera capture
    G.cam = cv2.VideoCapture(0)
    G.camThread = Thread(target=W.cvloop)
    G.camThread.start()

    # Flask Server
    F.server.start()


