#!/usr/bin/env python

from collections import deque
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
import signal
import os
import re
import Tkinter as tk
from threading import Thread, RLock

# Globals
stop=False
helpTextOn=False
cam=None
root=None
frameLock=RLock()
camLock=RLock()
cvFrame=None
uiFrame=None
renderMode='t'
calOpts=['h1','h2','s','v','kern','blur','bright']
calSet=[20,160,80,80,5,5,2]
calTops=[180,180,255,255,10,10,3]
calBots=[0,0,0,0,1,1,1]
calSelected=0
cvFrameN=0
uiFrameN=0
frameW=640
frameH=480
frameTimes = deque([0]*20)
fps=0.0
dbg_lock=False
dbg_can=False
dbg_key=False
dbg_file=True
calibFname="calib.py"

#----------------------------------------------------------------------

def purge_pyc():
    global dbg_file
    folder=os.path.dirname(os.path.realpath(__file__))
    pat=".*\.pyc"
    if dbg_file: print "Purging .pyc files"
    for f in os.listdir(folder):
        if re.search("^.*\.pyc$",f):
            os.remove(os.path.join(folder,f))

def quit_(root):
    root.destroy()

def cvloop():
    global cvFrame, cvFrameN
    cvFrame = np.zeros((frameH,frameW,3), np.uint8)
    cvFrameN+=1
    while True:
        if dbg_lock: print "cvloop wait camLock... ",
        with camLock:
            if dbg_lock: print "using lock"
            ret, f = cam.read()
        #time.sleep(0.25)
        if stop: break
        if dbg_lock: print "cvloop wait frameLock... ",
        with frameLock:
            if dbg_lock: print "using lock"
            cvFrame = f
            cvFrameN+=1
        if stop: break
    print "camera shutdown"

def update_image(image_label, cam):
    global uiFrame, calSet, dbg_can
    (h1, h2, s, v, cSiz, bSiz, bright) = calSet
    f = uiFrame
    f = cv2.resize(f, (640,480)) 
    #
    img = f
    #img = cv2.blur(img, (bSiz,bSiz))
    img = cv2.medianBlur(img, 1+2*(bSiz-1))
    #
    # Increase intensity such that
    # dark pixels become much brighter, 
    # bright pixels become slightly bright
    maxIntensity = 255.0 # depends on dtype of image data
    phi = 1
    theta = 1
    img = (maxIntensity/phi)*(img/(maxIntensity/theta))**(1.0/bright)
    img = np.array(img,dtype=np.uint8)
    #
    # Thresholding
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    thresha = cv2.inRange(hsv,np.array((h2, s, v)), np.array((180, 255, 255)))
    threshb = cv2.inRange(hsv,np.array((0, s, v)), np.array((h1, 255, 255)))
    thresh = cv2.bitwise_or(thresha, threshb)
    # Morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(cSiz,cSiz))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(cSiz*1.5),int(cSiz*1.5)))
    cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel,thresh)
    cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel,thresh)
    cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel2,thresh)
    cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel2,thresh)
    # Contours
    thresh2 = thresh.copy()
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    best_cnt = None
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if (area > max_area and area > (30*30)):
            max_area = area
            best_cnt = cnt
    if renderMode == 't':
        threshImg = cv2.cvtColor(thresh2, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_or(threshImg, img)
    if (best_cnt != None):
        M = cv2.moments(best_cnt)
        cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        cv2.circle(img,(cx,cy),5,255,-1)
        x,y,w,h = cv2.boundingRect(best_cnt)
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
        minRect = cv2.minAreaRect(best_cnt)
        minRect = np.int0(cv2.cv.BoxPoints(minRect))
        cv2.drawContours(img,[minRect],0,(0,255,255),1)
        if dbg_can: print "can cx=", cx, "cy=", cy,
    else:
        if dbg_can: print "no target",
    if dbg_can: print "h1", h1, "h2", h2, "s", s, "v", v
    #
    # Convert image format
#    #img = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
#    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if helpTextOn: img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else: img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #
    a = Image.fromarray(img)
    b = ImageTk.PhotoImage(image=a)
    image_label.configure(image=b)
    image_label._image_cache = b  # avoid garbage collection
    root.update()
    #cv2.imshow('frame',f)
    

def update_fps(fps_label):
    global fps, calSet, calOpts, calSelected, frameTimes
    frameTimes.rotate()
    frameTimes[0] = time.time()
    sum_of_deltas = frameTimes[0] - frameTimes[-1]
    count_of_deltas = len(frameTimes) - 1
    try:
        fps = float(count_of_deltas) / sum_of_deltas
    except ZeroDivisionError:
        fps = 0
    #ltext='FPS: %.2f  '%(fps)
    ltext=""
    for i in xrange(len(calSet)):
        if i==calSelected: 
            ltext += " |%s: %d|"%(calOpts[i], calSet[i])
        else: 
            ltext += "  %s: %d "%(calOpts[i], calSet[i])
    fps_label.configure(text=ltext)
    root.wm_title("PringleCV - %.2f fps"%(fps))

def sigint_handler(signum, frame):
    print "Keyboard or Signal interrupt"
    root.destroy()

def key_ctrl_s(event):
    global calSet, calibFname, dbg_file
    fname = calibFname
    if dbg_file: print "writing", fname
    fil = open(fname, 'w')
    fil.write('# Calibration settings for PringleCV\n')
    fil.write('calSet='+str(calSet)+'\n')

def key_handler(event):
    global renderMode, calSet, calSelected, calOpts, calTops, dbg_key, helpTextOn
    if dbg_key: print "keybd:", event.type, event.keycode, "...",
    if (event.char == 'q' or event.keysym == "Escape"):
        if dbg_key: print "exit"
        root.destroy()
    elif event.char == 's':
        if dbg_key: print "src image"
        renderMode = 's'
    elif event.char == 't':
        if dbg_key: print "target image"
        renderMode = 't'
    elif event.char == 'h':
        if dbg_key: print "help text toggle"
        helpTextOn = not helpTextOn
    elif event.keysym == "Left":
        prop = calSelected-1
        if prop>=0:
            if dbg_key: print "select property", prop, "-", calOpts[prop]
            calSelected = prop
    elif event.keysym == "Right":
        prop = calSelected+1
        if prop<len(calSet):
            if dbg_key: print "select property", prop, "-", calOpts[prop]
            calSelected = prop
#    elif event.char.isdigit():
#        prop = int(event.char)-1
#        print "set property", prop,
#        if (0 <= prop < len(calSet)):
#            print "-", calOpts[prop]
#            calSelected = prop
#        else:
#            print "- property does not exist"
    elif event.keysym == "Up":
        calSet[calSelected] = min(calSet[calSelected]+1, calTops[calSelected])
        if dbg_key: print "set", calOpts[calSelected], "to", calSet[calSelected]
    elif event.keysym == "Down":
        calSet[calSelected] = max(calSet[calSelected]-1, calBots[calSelected])
        if dbg_key: print "set", calOpts[calSelected], "to", calSet[calSelected]
    else:
        if dbg_key: print "nothing"

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
    # Config files
    purge_pyc()
    try:
        mod_calib = __import__("calib")
        calSet = mod_calib.calSet
    except ImportError:
        if dbg_file: print "Note: calib.py doesn't exist yet"
    purge_pyc()

    # Camera source
    cam = cv2.VideoCapture(0) 

    # Main window
    root = tk.Tk() 
    root.geometry("+%d+%d"%(0,0))
    root.wm_title("PringleCV")

    # Bindings
    root.bind_all('<Key>',key_handler)
    root.bind_all('<Control-s>',key_ctrl_s)
    signal.signal(signal.SIGINT, sigint_handler)

    # Widgets
    image_label = tk.Label(master=root)# label for the video frame
    image_label.pack()
    fps_label = tk.Label(master=root, font="TkFixedFont")
    fps_label.pack()
    #quit_button = tk.Button(master=root, text='Quit',command=lambda: quit_(root))
    #quit_button.pack()

    # Threads
    thread = Thread(target = cvloop)
    thread.start()

    # Main loops
    root.after(20, func=lambda: update_all(root, image_label, cam, fps_label))
    root.mainloop()

    # finish
    stop=True
    thread.join()
    cam.release()
    cv2.destroyAllWindows()
