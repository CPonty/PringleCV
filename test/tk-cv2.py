#!/usr/bin/env python

from collections import deque
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
import Tkinter as tk
from threading import Thread, RLock

stop=False
cam=None
root=None
frameLock=None
cvFrame=None
uiFrame=None
cvFrameN=0
uiFrameN=0
frameW=640
frameH=480
fps=0.0
dbg_lock=False

def quit_(root):
    root.destroy()

def cvloop():
    global cvFrame, cvFrameN
    cvFrame = np.zeros((frameH,frameW,3), np.uint8)
    cvFrameN+=1
    while True:
        ret, f = cam.read()
        #time.sleep(0.25)
        if stop: break
        if dbg_lock: print "cvloop wait... ",
        with frameLock:
            if dbg_lock: print "using lock"
            cvFrame = f
            cvFrameN+=1
        if stop: break
    print "stop cvloop"

def update_image(image_label, cam):
    global uiFrame
    f = uiFrame
    f = cv2.resize(f, (640,480)) 
    #
    img = f
    img = cv2.blur(img, (5,5))
    #
    # Increase intensity such that
    # dark pixels become much brighter, 
    # bright pixels become slightly bright
    maxIntensity = 255.0 # depends on dtype of image data
    phi = 1
    theta = 1
    img = (maxIntensity/phi)*(img/(maxIntensity/theta))**0.4
    img = np.array(img,dtype=np.uint8)
    #
#    #img = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #
    a = Image.fromarray(img)
    b = ImageTk.PhotoImage(image=a)
    image_label.configure(image=b)
    image_label._image_cache = b  # avoid garbage collection
    root.update()
    #cv2.imshow('frame',f)
    

def update_fps(fps_label):
    global fps
    frame_times = fps_label._frame_times
    frame_times.rotate()
    frame_times[0] = time.time()
    sum_of_deltas = frame_times[0] - frame_times[-1]
    count_of_deltas = len(frame_times) - 1
    try:
        fps = float(count_of_deltas) / sum_of_deltas
    except ZeroDivisionError:
        fps = 0
    fps_label.configure(text='FPS: %.2f'%(fps))


def update_all(root, image_label, cam, fps_label):
    global cvFrameN, uiFrameN, cvFrame, uiFrame, fps
    #print "cv=", cvFrameN, "ui=", uiFrameN, "fps=", "%.2f"%(fps)
    if (cvFrameN > uiFrameN): 
        if dbg_lock: print "update_all wait... ",
        with frameLock:
            if dbg_lock: print "using lock"
            uiFrame=cvFrame    
            uiFrameN=cvFrameN
        update_image(image_label, cam)
        update_fps(fps_label)
    root.after(0, func=lambda: update_all(root, image_label, cam, fps_label))


if __name__ == '__main__':
    root = tk.Tk() 
    image_label = tk.Label(master=root)# label for the video frame
    image_label.pack()
    cam = cv2.VideoCapture(0) 
    fps_label = tk.Label(master=root)# label for fps
    fps_label._frame_times = deque([0]*20)  # arbitrary 20 frame average FPS
    fps_label.pack()
    quit_button = tk.Button(master=root, text='Quit',command=lambda: quit_(root))
    quit_button.pack()

    # setup the frame grabbing thread
    frameLock = RLock()
    thread = Thread(target = cvloop)
    thread.start()

    # setup the update callback
    root.after(20, func=lambda: update_all(root, image_label, cam, fps_label))
    root.mainloop()

    stop=True
    thread.join()
    cam.release()
    cv2.destroyAllWindows()
