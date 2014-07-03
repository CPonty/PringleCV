# demonstration of python + OpenCV: webcam streaming
# http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html

from time import time, sleep
import numpy as np
import cv2

cap = cv2.VideoCapture(0)

print "Press 'q' to quit"

t = [time()]
fps=0
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert Gray
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 

    t.append(time())
    if len(t)>30: 
        t.pop(0)
        fps = len(t) / (t[-1] - t[0])
        print "fps=", fps

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    sleep(0.05)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
