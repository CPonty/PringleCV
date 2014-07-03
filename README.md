PringleCV
==========

An OpenCV-based computer vision system inspired by ReacTIVision.

PringleCV was designed for students of UQ's *CSSE3010 - Embedded Systems Design & Interfacing* course.

It provides the capability to track and localise a painted, labelled can (mounted on a rover vehicle) in 3D space
using a single, low-cost webcam. Telemetry is available to external agents via UDP broadcast, a TCP server and
a publish/subscribe topic on a Mosquitto server (MQTT).

PringleCV consists of 3 applications:

 - `webcam.py` - tracking via computer vision

 - `telemetry.py` - distributing telemetry data

 - `webserver.py`- 3D visualisation of the position using WebGL
