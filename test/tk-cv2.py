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
from threading import Thread, RLock, Event

# Globals
stop=False
helpTextOn=False
captureEvent=Event()
cam=None
root=None
frameLock=RLock()
camLock=RLock()
cvFrame=None
uiFrame=None
renderMode='s'
calOpts=['h0','h1','s0','s1','v0','v1','kern','lumina','hue','sat','val',
        'poly2hull','hull2bbox']
calSet=[170,5,80,255,100,255,5,0,0,0,0,75,75]
calTops=[180,180,255,255,255,255,10,1,5,5,5,100,100]
calBots=[0,0,0,0,0,0,1,0,-5,-5,-5,0,0]
calSelected=0
cvFrameN=0
uiFrameN=0
frameW=640
frameH=480
frameTimes = deque([0]*20)
canWidths = deque([0]*5)
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
    global cvFrame, cvFrameN, pauseEvent
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
        captureEvent.wait()
        if stop: break
    print "camera shutdown"

def update_image(image_label, cam):
    global uiFrame, calSet, dbg_can, frameW, frameH
    (h0,h1,s0,s1,v0,v1,cSiz,lumina,hue,sat,val,p2h,h2b) = calSet[0:13]
    f = uiFrame
    f = cv2.resize(f, (640,480)) 
    #
    img = f
    #img = cv2.blur(img, (bSiz,bSiz))
    img = cv2.medianBlur(img, 5)
    #
#    # brightness rebalancing # don't do it - woefully inefficient
#    maxIntensity = 255.0 # depends on dtype of image data
#    phi = 1
#    theta = 1
#    if (bright==2 or bright==4):
#        img = np.array(
#            (maxIntensity/phi)*(img/(maxIntensity/theta))**(1.0/bright),
#        dtype=np.uint8)
#    #
    # Histogram equalization
    # YCrCb color space: y=lumina, Cr/Cb = chroma. Suits digital images
    if lumina>0:
        YCrCb = cv2.cvtColor(img,cv2.cv.CV_BGR2YCrCb)
        channels = cv2.split(YCrCb)
        channels[0] = cv2.equalizeHist(channels[0])
        YCrCb = cv2.merge(channels)
        img = cv2.cvtColor(YCrCb,cv2.cv.CV_YCrCb2BGR)
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    if (hue!=0 or sat!=0 or val!=0): 
        channels = cv2.split(hsv)
        if (hue>0): channels[0] = channels[0]
        if (sat>0): channels[1] = channels[1]
        if (val>0): channels[2] = channels[2]
        hsv = cv2.merge(channels)
        img = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    #
    # Thresholding - account for h0 > h1
    if h0 < h1:
        thresh = cv2.inRange(hsv,np.array((h0,s0,v0)), np.array((h0,s1,v1)))
    else:
        thresha = cv2.inRange(hsv,np.array((h0,s0,v0)), np.array((255,s1,v1)))
        threshb = cv2.inRange(hsv,np.array((0,s0,v0)), np.array((h1,s1,v1)))
        thresh = cv2.bitwise_or(thresha, threshb)
    # Morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(cSiz,cSiz))
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(cSiz*1.5),int(cSiz*1.5)))
    cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel,thresh)
    cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel,thresh)
    #cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel2,thresh)
    cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel2,thresh)
    # Contours
    thresh2 = thresh.copy()
    #cv2.RETR_EXTERNAL - ignores inner edge & interior shapes
    #cv2.RETR_LIST - default
    #cv2.RETR_LIST - exterior lines in hierachy 1, interior in hierachy 2
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    best_cnt = None
    bestCntHullArea = 0
#    bestCntPolyArea = 0
#    bestCntBboxArea = 0
    cntCandidates = []
    for i,cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        # ignoring obvious fails will save a lot of processing power
        if hierarchy[0,i,3]!=-1: continue #top-level contour, parent==-1
        if (w<25 or h<25 or area<(25*25)): continue
        hull = cv2.convexHull(cnt)
        hullArea = cv2.contourArea(hull)
        minRect = cv2.minAreaRect(cnt)
        minRect = np.int0(cv2.cv.BoxPoints(minRect))
        bboxCnt = cv2.convexHull(minRect)
        bboxArea = cv2.contourArea(bboxCnt)
        cntArcLen = cv2.arcLength(cnt,True)
        poly = cv2.approxPolyDP(cnt,0.01*cntArcLen,True)
        polyArea = cv2.contourArea(poly)
        hullVsBbox = float(hullArea)/bboxArea*100
        polyVsHull = float(polyArea)/hullArea*100
        polyVsBbox = float(polyArea)/bboxArea*100
        # ensure dimensions and area are valid
        if (hullVsBbox>h2b and polyVsHull>p2h):
            # only replace if it's bigger
            if (hullArea > bestCntHullArea):
                bestCntHullArea = hullArea
#                bestCntPolyArea = polyArea
#                bestCntBboxArea = bboxArea
                best_cnt = cnt
        cntCandidates.append(cnt)
    # Final threshold image
    if renderMode == 't':
        cv2.drawContours(img,cntCandidates,-1,(255,255,255),cv2.cv.CV_FILLED)
#        threshFinal = np.zeros((frameH,frameW,1), np.uint8)
#        cv2.drawContours(threshFinal,cntCandidates,-1,(255),
#                thickness=cv2.cv.CV_FILLED)
#        threshImg = cv2.cvtColor(threshFinal, cv2.COLOR_GRAY2BGR)
#        img = cv2.bitwise_or(threshImg, img)

    # Contour post-processing
    print len(cntCandidates)
    if (best_cnt != None):
        M = cv2.moments(best_cnt)
        cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
        cv2.circle(img,(cx,cy),5,(0,255,0),-1)
        x,y,w,h = cv2.boundingRect(best_cnt)
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),1)
        minRect = cv2.minAreaRect(best_cnt)
        minRect = np.int0(cv2.cv.BoxPoints(minRect))
        cv2.drawContours(img,[minRect],0,(0,255,255),2)
        hull = cv2.convexHull(best_cnt)
        cv2.drawContours(img,[hull],0,(255,255,0),2)
        bestCntArc = cv2.arcLength(best_cnt,True)
        approxPoly = cv2.approxPolyDP(best_cnt,0.01*bestCntArc,True)
        cv2.drawContours(img,[approxPoly],0,(255,0,255),2)
        if dbg_can: print "can cx=", cx, "cy=", cy,
    else:
        if dbg_can: print "no target",
    if dbg_can: print "h1", h1, "h2", h2, "s", s, "v", v
    #
    # Convert image format
#    #img = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    if helpTextOn: img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else: img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #
    imDraw = Image.fromarray(img)
    imDraw2 = ImageTk.PhotoImage(image=imDraw)
    image_label.configure(image=imDraw2)
    image_label._image_cache = imDraw2  # avoid garbage collection - important!
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
    ltext=''
    for i in xrange(len(calSet)):
        if i==calSelected: 
            ltext += " |%s: %d|"%(calOpts[i], calSet[i])
        else: 
            ltext += "  %s: %d "%(calOpts[i], calSet[i])
        if (i!=0 and i%7==0):
            ltext += '\n\n'
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
    global renderMode, calSet, calSelected, calOpts, calTops, dbg_key, \
    helpTextOn, captureEvent
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
    elif event.char == 'p':
        if captureEvent.isSet(): captureEvent.clear()
        else: captureEvent.set()
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

    # Camera source
    cam = cv2.VideoCapture(0) 

    # Main window
    root = tk.Tk() 
    root.geometry("+%d+%d"%(0,0))
    root.resizable(width=False, height=False)
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
    captureEvent.set()

    # Main loops
    root.after(20, func=lambda: update_all(root, image_label, cam, fps_label))
    root.mainloop()

    # finish
    stop=True
    captureEvent.set() #allows the capture thread to unblock if paused
                       #while blocking it can't see stop=True, so join() hangs
    thread.join()
    cam.release()
    cv2.destroyAllWindows()
    purge_pyc()
