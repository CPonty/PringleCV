#!/usr/bin/env python

# Demonstration of OpenCV Backprojection


#import matplotlib
#matplotlib.use('GTKAgg') #avoid clashing GTK versions with OpenCV
#import matplotlib.pyplot as plt

from math import degrees, radians
from time import time, sleep
import numpy as np
import cv2
import sys
import os
import re

def purge_pyc():
    global dbg_file
    folder=os.path.dirname(os.path.realpath(__file__))
    pat=".*\.pyc"
    for f in os.listdir(folder):
        if re.search("^.*\.pyc$",f):
            os.remove(os.path.join(folder,f))

purge_pyc()
from cvcommon import *
purge_pyc()

cap = cv2.VideoCapture(0)
print "Press 'q' to quit"

FPS_PRINT=True
BLOB_TRACK=True
HIST_RESAMPLE=True
HIST_PLOT=False
HIST_FRAC=0.5
HIST_MIN_STRENGTH=5
HIST_ROI_DILATION=0
HIST_SAMP_DILATION=0
HSV_H0=3
HSV_H1=171
HSV_S0=0
HSV_S1=30
HSV_S2=60
HSV_V0=55
K1SIZE=5
K2SIZE=10
threshVal=60

t = [time()]
fps=0
f=0
(xx,yy,ww,hh) = (640/2-60,480/2-80,120,160)
src=5
grab=False
im=None
imArray=[None]*8
roi=None
roiHist=None
roiHist2=None
hist2=np.zeros((180,256),np.uint8)
trackingHist=None
drawBox=False
pause=False
histBar = np.zeros((5,256),np.uint8)
histBar.fill(255)

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

def keyboard(waitFor):
    global pause, src, threshVal, grab, HIST_MIN_STRENGTH, HIST_ROI_DILATION, \
        HIST_SAMP_DILATION
    k = (cv2.waitKey(waitFor) & 0xFF)
    if k == ord('q'):
        return True
    elif ( ord('1')<=k<=ord('6')):
        src=k-ord('0')
        print 'source',src
    elif k == ord('p'):
        pause = not(pause)
    elif k == ord('g'):
        grab=True
        if pause: 
            src=2
            print "done"
        else: 
            src=1
            print 'sampling...',
            sys.stdout.flush()
        pause = not(pause)
    elif k == ord('['):
        HIST_ROI_DILATION = max(0,HIST_ROI_DILATION-1)
        print "HIST_ROI_DILATION=", HIST_ROI_DILATION
    elif k == ord(']'):
        HIST_ROI_DILATION = min(255,HIST_ROI_DILATION+2)
        print "HIST_ROI_DILATION=", HIST_ROI_DILATION
    elif k == ord('-'):
        HIST_SAMP_DILATION = max(0,HIST_SAMP_DILATION-1)
        print "HIST_SAMP_DILATION=", HIST_SAMP_DILATION
    elif k == ord('='):
        HIST_SAMP_DILATION = min(255,HIST_SAMP_DILATION+2)
        print "HIST_SAMP_DILATION=", HIST_SAMP_DILATION
    return False

def display():
    global imArray,pause,xx,yy,ww,hh,src
    # Display the resulting frame
    imArray[1] = imArray[0].copy()
    cv2.rectangle(imArray[1],(xx,yy),(xx+ww,yy+hh),(0,255,0),2)
    cv2.imshow('im',imArray[src])
    if trackingHist!=None: 
#        print "shapes:",roiHist2.shape, histBar.shape, hist2.shape, trackingHist.shape
#        sys.stdout.flush()
        cv2.imshow('hist(roi,hist2,track)',np.vstack((roiHist2,histBar,hist2,histBar,trackingHist)))

#----------------------------------------------------------------------

cv2.namedWindow('im')
cv2.namedWindow('hist(roi,hist2,track)')
cv2.setMouseCallback('im',mouseclick)

trackingHist=np.zeros((180,256),np.uint8)
hist=np.zeros((180,256),np.uint8)
hist2=np.zeros((180,256),np.uint8)
roiHist=np.zeros((180,256),np.uint8)
roiHist2=np.zeros((180,256),np.uint8)
#cv2.rectangle(trackingHist,(140,175),(250,180),255,-1)
#cv2.rectangle(trackingHist,(140,0),(250,2),255,-1)
#cv2.rectangle(trackingHist,(40,75),(250,180),255,-1)
#cv2.rectangle(trackingHist,(40,0),(250,92),255,-1)

roiHist2= cv2.calcHist(np.zeros((480,640),np.uint8),[0,1], None, [180,256], [0,180,0,256])
roiHist2[:,:] = 0
cv2.rectangle(roiHist2,(140,174),(250,180),255,-1)
cv2.rectangle(roiHist2,(140,0),(250,3),255,-1)
trackingHist=roiHist2.copy()

#print "max",np.max(trackingHist),"shape",trackingHist.shape
#cv2.imshow('trackhist',trackingHist)
#keyboard(5000)
#sys.exit()

while(True):
    if keyboard(1): break
    if imArray[src]!=None: display()
    if pause: 
#        keyboard(100)
        continue

    # Grab RoI
    if (grab==True and imArray[0]!=None and ww>2 and hh>2):
        roi = im[yy:yy+hh, xx:xx+ww]
        hsv = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        roiHist= cv2.calcHist([hsv],[0,1], None, [180,256], [0,180,0,256])
        roiHist[HSV_H0:HSV_H1,:] = 0
        roiHist[:,HSV_S0:HSV_S1] = 0
        for i in xrange(HSV_S1,HSV_S2):
            roiHist[:,i] *= float(i-HSV_S1)/(HSV_S2-HSV_S1)
        roiHist[roiHist < HIST_MIN_STRENGTH] = 0
        roiHist2= roiHist.copy()
        print "max",np.max(roiHist2),"mean",np.mean(roiHist2)
        cv2.normalize(roiHist2,roiHist2,0,255,cv2.NORM_MINMAX)
        print "max",np.max(roiHist2),"mean",np.mean(roiHist2)
        trackingHist = roiHist.copy()
        #plot histogram. gotta go fast!
        if HIST_PLOT: 
            plt.imshow(roiHist,interpolation = 'nearest')
            plt.show()
        #
        grab=False
        src=2
        

    # Capture frame-by-frame
    ret, im = cap.read()
    im = cv2.medianBlur(im, 5)
    imArray=[im.copy() for i in xrange(len(imArray))]

    t.append(time())
    if len(t)>30: 
        t.pop(0)
        fps = len(t) / (t[-1] - t[0])
        f+=1
        if (FPS_PRINT and f%10==0): print "fps=", fps

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
        hue,sat,val = cv2.split(hsvt)
        #print "hist avg",np.mean(trackingHist)
        dst = cv2.calcBackProject([hsvt],[0,1],trackingHist,[0,180,0,256],1)
        # Now convolute with circular disc
        disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        cv2.filter2D(dst,-1,disc,dst)
        #print "dst max",np.max(dst),"hist avg",np.mean(trackingHist)
#TODO minimum brightness
        vmask = val.copy()
        vmask[vmask < HSV_V0] = 0
        vmask[vmask > 0] = 255
        dst= cv2.bitwise_and(dst, vmask)

        # threshold and binary AND
        imArray[2] = dst #grayscale distance
        ret,thresh = cv2.threshold(dst,threshVal,255,0)
        imArray[3] = thresh
        thresh3 = cv2.merge((thresh,thresh,thresh)) #threshold, 3-channel
        img4 = cv2.bitwise_and(im,thresh3) #combined image
        imArray[4] = img4
        #res = np.vstack((target,thresh,res))

        #test: blob tracking; redo the histogram
        # BLOB_TRACK #
        if BLOB_TRACK==False: continue
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(K1SIZE,K1SIZE))
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(K2SIZE,K2SIZE))
        cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel,thresh)
        cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,kernel,thresh)
        cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel2,thresh)
        thresh2 = thresh.copy()
        contours,hierarchy = cv2.findContours(thresh,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        best_cnt = None
        bestCntHullArea = 0
        cntCandidates = []
        for i,cnt in enumerate(contours):
            area = cv2.contourArea(cnt)
            x,y,w,h = cv2.boundingRect(cnt)
            # ignoring obvious fails will save a lot of processing power
            if hierarchy[0,i,3]!=-1: continue #top-level contour, parent==-1
            if (w<20 or h<20 or (w*h<25*25) or area<(20*20)): continue
            hull = cv2.convexHull(cnt)
            hullArea = cv2.contourArea(hull)
            minRect = cv2.minAreaRect(cnt)
            minRect = np.int0(cv2.cv.BoxPoints(minRect))
            bboxCnt = cv2.convexHull(minRect)
            bboxArea = cv2.contourArea(bboxCnt)
            cntArcLen = cv2.arcLength(cnt,True)
            cntArea = cv2.contourArea(cnt)
            hullVsBbox = float(hullArea)/bboxArea*100
            cntVsHull = float(cntArea)/hullArea*100
            cntVsBbox = float(cntArea)/bboxArea*100
            # only replace if it's bigger
            if (hullArea > bestCntHullArea):
                bestCntHullArea = hullArea
                best_cnt = cnt
            cntCandidates.append(cnt)
        #cv2.drawContours(img4,cntCandidates,-1,(255,255,255),cv2.cv.CV_FILLED)
        cv2.drawContours(img4,cntCandidates,-1,(255,0,255),thickness=1)
        cv2.drawContours(imArray[5],cntCandidates,-1,(255,0,255),thickness=1)
        #print len(cntCandidates)
        if (best_cnt != None):
            x,y,w,h = cv2.boundingRect(best_cnt)
            cv2.rectangle(img4,(x,y),(x+w,y+h),(0,255,0),1)
            cv2.rectangle(imArray[5],(x,y),(x+w,y+h),(0,255,0),1)
            cv2.rectangle(imArray[6],(x,y),(x+w,y+h),(0,255,0),1)
            minRect = cv2.minAreaRect(best_cnt)
            minRect = np.int0(cv2.cv.BoxPoints(minRect))
            #print "minRect:", minRect
            #minRectWline = 
            #print "minRectW:", 
            #cv2_minRectW(minRect)
            cv2.drawContours(img4,[minRect],0,(0,255,255),1)
            cv2.drawContours(imArray[5],[minRect],0,(0,255,255),1)
            cv2.drawContours(imArray[6],[minRect],0,(0,255,255),2)
            (canw,canh),wl,hl = cv2_minRectAxes(minRect)
            cv2.line(imArray[6],wl[0],wl[1],cv2_yellow,2)
            hull = cv2.convexHull(best_cnt)
            cv2.drawContours(img4,[hull],0,(255,255,0),1)
            cv2.drawContours(imArray[5],[hull],0,(255,255,0),1)
            cv2.drawContours(imArray[6],[hull],0,(255,255,0),1)
            bestCntArc = cv2.arcLength(best_cnt,True)
            (ex,ey),(eMa,ema),eAngle = cv2.fitEllipse(best_cnt)
            M = cv2.moments(best_cnt)
            cx,cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cv2.circle(img4,(cx,cy),5,(0,255,0),-1)
            cv2.circle(imArray[5],(cx,cy),5,(0,255,0),-1)
            cv2.circle(imArray[6],(cx,cy),5,(0,255,0),-1)
            #print "circle:",(ex,ey),(eMa,ema),eAngle
            #load new images
            imArray[3] = thresh2
            imArray[4] = img4
            # HIST_RESAMPLE #
            if HIST_RESAMPLE==False: continue
            #create mask of best_cnt & resample a new RoI (hull area)
            hsv = cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
            mask = np.zeros((hsv.shape[0],hsv.shape[1],1),np.uint8)
            cv2.drawContours(mask,[best_cnt],0,255,-1)
            #cv2.drawContours(mask,[hull],0,255,-1)
#TODO - erode sample mask & delete small blobs again
            imArray[7] = mask.copy()
            #pixelpoints = np.transpose(np.nonzero(mask))
            #resample RoI
            hist2 = cv2.calcHist([hsv],[0,1], mask, [180,256], [0,180,0,256])
            print "h2max",np.max(hist2),"h2shape",hist2.shape
            hist2[HSV_H0:HSV_H1,:] = 0
            hist2[:,HSV_S0:HSV_S1] = 0
            cv2.normalize(hist2,hist2,0,255,cv2.NORM_MINMAX)
#TODO - apply distance (roiHist, hist2) to hist2
            #gradient-scale the saturation weighting in the resampled hist
            for i in xrange(HSV_S1,HSV_S2):
                hist2[:,i] *= float(i-HSV_S1)/(HSV_S2-HSV_S1)
            #hist2n = hist2.copy()
            #cv2.normalize(hist2n,hist2n,0,255,cv2.NORM_MINMAX)
            cv2.normalize(hist2,hist2,0,255,cv2.NORM_MINMAX)
            roiHist2Sum = cv2.sumElems(roiHist2)[0]
            if (roiHist2Sum > 0):
                hist2Sum = cv2.sumElems(hist2)[0]
                histRatio = 1.*hist2Sum / roiHist2Sum
                hist2Frac = 1.*hist2Sum / (hist2Sum+roiHist2Sum)
                if (hist2Frac>HIST_FRAC):
                    t1=time()
                    hist2*=((1.-hist2Frac)/hist2Frac)*(HIST_FRAC/(1.-HIST_FRAC))
                    t2=time()
#                print "time taken to equalize:", t2-t1
            hist2[hist2 < HIST_MIN_STRENGTH] = 0
#            if histRatio>1:
#                hist2 *= 1./histRatio
            hist2Sum2 = cv2.sumElems(hist2)[0]
#            print "SumRoi",int(roiHist2Sum),"SumHist2",int(hist2Sum),"ratio",histRatio,"sumAfter",int(hist2Sum2)
            ##cv2.normalize(roiHist2,roiHist2,0,255,cv2.NORM_MINMAX)
            ##cv2.normalize(hist2,hist2,0,255,cv2.NORM_MINMAX)

            # balance original sample and resample histograms
            #if (roiHist2Sum>1 and hist2Sum > roiHist2Sum):
            #    trackingHist = cv2.add(roiHist2*histRatio, hist2)
            #else:
            #    trackingHist = cv2.add(roiHist2, hist2)
            #print "roiHist2Sum:", int(roiHist2Sum), "hist2Sum:", int(hist2Sum)
            trackingHist = cv2.add(roiHist2, hist2)/2
            
            #zero the histogram outside the hue/sat bounds
            #y,x  y:hue x:sat
            ##trackingHist[HSV_H0:HSV_H1,:] = 0
            ##trackingHist[:,HSV_S0:HSV_S1] = 0
            #
#            cv2.normalize(trackingHist,trackingHist,0,255,cv2.NORM_MINMAX)
#TODO mandatory match - certain band of red
            #cv2.rectangle(trackingHist,(140,175),(250,180),255,-1)
            #cv2.rectangle(trackingHist,(140,0),(250,2),255,-1)


#----------------------------------------------------------------------

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

