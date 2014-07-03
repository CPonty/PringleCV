#!/usr/bin/env python

from flask import Flask, request
from threading import Thread, Lock, RLock, Event, Timer
from multiprocessing import Process
from signal import signal, SIGINT
import sys
import cv2
import numpy as np
import atexit

#======================================================================

POOL_TIME = 0.1 #Seconds

# variables that are accessible from anywhere
G = {"a":1}
# lock to control access to variable
dataLock = Lock()
# thread handler
yourThread = Thread()

def create_app():
    app = Flask(__name__)

    def interrupt():
        global yourThread
        yourThread.cancel()

    def doStuff():
        global G
        global yourThread
        with dataLock:
            # Do your stuff with commonDataStruct Here
            G['a']+=1
            print G['a'],

        # Set the next thread to happen
        yourThread = Timer(POOL_TIME, doStuff, ())
        yourThread.start()

    def doStuffStart():
        # Do initialisation stuff here
        global yourThread
        # Create your thread
        yourThread = Timer(POOL_TIME, doStuff, ())
        yourThread.start()

    # Initiate
    doStuffStart()
    # When you kill Flask (SIGTERM), clear the trigger for the next thread
    atexit.register(interrupt)
    return app

app = create_app()

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0')