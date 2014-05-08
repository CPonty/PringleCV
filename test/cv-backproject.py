#!/usr/bin/env python

# Demonstration of OpenCV Backprojection

import matplotlib
matplotlib.use('GTKAgg') #avoid clashing GTK versions with OpenCV
import matplotlib.pyplot as plt

from time import time, sleep
import numpy as np
import cv2

cap = cv2.VideoCapture(0)

print "Press 'q' to quit"

t = [time()]
fps=0
f=0
(xx,yy,ww,hh) = (640/2-60,480/2-60,120,120)
src=1
grab=False
im=None
imArray=[None,None,None,None,None]
roi=None
roiHist=None
drawBox=False
pause=False
threshVal=50

def mouseclick(event,x,y,flags,param):
    global xx,yy,ww,hh,drawBox
    if event == cv2.EVENT_LBUTTONDOWN:
        xx,yy = x,y
        drawBox=True
    elif (event == cv2.EVENT_MOUSEMOVE and drawBox):
        ww,hh = x-xx,y-yy
    elif event == cv2.EVENT_LBUTTONUP:
        ww,hh = x-xx,y-yy
        drawBox = False

def keyboard():
    global pause, src, threshVal, grab
    k = (cv2.waitKey(1) & 0xFF)
    if k == ord('q'):
        return True
    elif ( ord('1')<=k<=ord('4')):
        src=k-ord('0')
        print 'source',src
    elif k == ord('p'):
        pause = not(pause)
    elif k == ord('g'):
        grab=True
        if pause: src=2
        else: src=1
        pause = not(pause)
        print 'sampling'
    elif k == ord('['):
        threshVal = max(0,threshVal-3)
        print "threshVal=", threshVal
    elif k == ord(']'):
        threshVal = min(255,threshVal+3)
        print "threshVal=", threshVal
    return False

def display():
    global imArray,pause,xx,yy,ww,hh,src
    # Display the resulting frame
    imArray[1] = imArray[0].copy()
    cv2.rectangle(imArray[1],(xx,yy),(xx+ww,yy+hh),(0,255,0),2)
    cv2.imshow('im',imArray[src])

#----------------------------------------------------------------------
cv2.namedWindow('im')
cv2.setMouseCallback('im',mouseclick)

while(True):
    if keyboard(): break
    if imArray[src]!=None: display()
    if pause: sleep(0.05); continue

    # Grab RoI
    if (grab==True and imArray[0]!=None):
        roi = im[yy:yy+hh, xx:xx+ww]
        hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        roiHist = cv2.calcHist([hsv],[0,1], None, [180,256], [0,180,0,256])
        cv2.normalize(roiHist,roiHist,0,255,cv2.NORM_MINMAX)
        grab=False
        src=2

    # Capture frame-by-frame
    ret, im = cap.read()
    im = cv2.medianBlur(im, 5)
    imArray=[im.copy() for i in xrange(5)]

    t.append(time())
    if len(t)>30: 
        t.pop(0)
        fps = len(t) / (t[-1] - t[0])
        f+=1
        if f%10==0: print "fps=", fps

    if (roiHist!=None):
    # Backproject
#         hsvt = cv2.cvtColor(im_s,cv2.COLOR_BGR2HSV)
#         I = cv2.calcHist([hsvt],[0, 1], None, [180, 256], [0, 180, 0, 256] )
#         R = M/(I+1) #hist ratios
#         h,s,v=cv2.split(hsvt)
#         B = R[h.ravel(),s.ravel()]
#         B = np.minimum(B,1)
#         B = B.reshape(hsvt.shape[:2])
#         disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
#         cv2.filter2D(B,-1,disc,B)
#         B = np.uint8(B)
#         cv2.normalize(B,B,0,255,cv2.NORM_MINMAX)
#         im_t = B
#         #ret,thresh = cv2.threshold(B,threshVal,255,0)
#         #thresh = cv2.cvtColor(thresh,cv2.COLOR_GRAY2BGR)#cv2.merge((thresh,thresh,thresh))
#         #im_t = cv2.bitwise_and(im_t,thresh)
#         #im_t = np.vstack((im_t,thresh,res))

        hsvt = cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsvt],[0,1],roiHist,[0,180,0,256],1)
        # Now convolute with circular disc
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        cv2.filter2D(dst,-1,disc,dst)
 
        # threshold and binary AND
        imArray[2] = dst #grayscale distance
        ret,thresh = cv2.threshold(dst,threshVal,255,0)
        imArray[3] = thresh
        thresh3 = cv2.merge((thresh,thresh,thresh)) #threshold, 3-channel
        imArray[4] = cv2.bitwise_and(im,thresh3) #combined image
        #res = np.vstack((target,thresh,res))

#----------------------------------------------------------------------

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
