#!/bin/bash
# Script to install dependencies of PringleCV on a CSSE3010 2014 VM.

# (1) Basics
cd /home/csse3010
echo "[INFO]  1  Basics"
echo "[INFO] 1.1 Installing Aptitude"
sudo apt-get -qq install aptitude <<< "Y"
echo "[INFO] 1.2 Installing Vim"
sudo aptitude -q install vim <<< "n
Y
"
echo "[INFO] 1.3 Installing python-dev package"
sudo aptitude -q install python-dev <<< "n
Y
Y
"
echo "[INFO] 1.4 Installing guvcview (for webcam testing)"
sudo apt-get -qq install guvcview

# (2) Python packages
echo "[INFO]  2  Python"
echo "[INFO] 2.1 Installing pip"
sudo apt-get -qq install python-pip
echo "[INFO] 2.2 Installing flask (webserver)"
sudo pip -q install flask
echo "[INFO] 2.3 Installing flask-socketio"
sudo pip -q install flask-socketio
echo "[INFO] 2.4 Installing mosquitto (mqtt)"
sudo pip -q install mosquitto

# (3) OpenCV
echo "[INFO]  3  Installing OpenCV"
version="2.4.8"
mkdir -p "OpenCV"
cd OpenCV
echo "[INFO] 3.1 Removing pre-installed clashing libraries"
sudo apt-get -qq remove ffmpeg x264 libx264-dev
echo "[INFO] 3.2 Installing dependenices"
sudo aptitude -q install libopencv-dev build-essential checkinstall cmake pkg-config yasm libtiff4-dev libjpeg-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev python-dev python-numpy libtbb-dev libqt4-dev libgtk2.0-dev libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 v4l-utils ffmpeg <<< "n
n
n
Y
Y
"
echo "[INFO] 3.3 Downloading OpenCV-$version"
wget -O OpenCV-$version.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/$version/opencv-"$version".zip/download
echo "[INFO] 3.4 Extracting files"
unzip OpenCV-$version.zip
cd opencv-$version
mkdir -p build
cd build
echo "[INFO] 3.5 Preparing cmake build"
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON -D WITH_QT=OFF -D WITH_OPENGL=OFF ..
echo "[INFO] 3.6 Compiling C/C++"
make -j2
echo "[INFO] 3.7 Installing OpenCV"
sudo make install
sudo sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig
cd ../..
echo "[INFO]     OpenCV-$version installed"
echo "[INFO]     Size of $(pwd): $(du -sh .)"
echo "[INFO]"
echo "[INFO]     Installation finished." 
echo "[INFO]     Please ensure installed libraries are working"




#sudo pip install virtualenv
#if [ -z "$(grep 'PIP_' ~/.bashrc)" ] || [ ! -f ~/.bashrc ]; then
#echo "
## pip should only run if there is a virtualenv currently activated
#export PIP_REQUIRE_VIRTUALENV=true
## cache pip-installed packages to avoid re-downloading
#export PIP_DOWNLOAD_CACHE=$HOME/.pip/cache
## install with pip outside virtual environment
#syspip(){
#   PIP_REQUIRE_VIRTUALENV=\"\" pip \"\$@\"
#}" >> ~/.bashrc
#fi
#source ~/.bashrc
#mkdir virtualenv
#cd virtualenv
#virtualenv pringlevm
#. pringlevm/bin/activate

#if [ -z "$(grep 'PIP_' ~/.bashrc)" ] || [ ! -f ~/.bashrc ]; then
#echo "" >> ~/.bashrc
#fi
