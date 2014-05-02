#!/bin/bash
# Script to install PringleCV dependencies & tools for CSSE3010 on a Lubuntu 13.X VM.
# Script URL: https://raw.githubusercontent.com/CPonty/PringleCV/master/scripts/setup-lubuntu-1310.sh
# OpenCV on Ubuntu: http://help.ubuntu.com/community/OpenCV

#      1 2 3 4 5 6 7
steps=(y y y y y y n)
#------------------------------------------------------------------------------------
info () { echo "[INFO] $1"; }
cd /home/csse3010

# (1) Basics
[[ "${steps[1]}" == "y" ]] && {
info "===Basics==="
dependencies1=('mosquitto' 'mosquitto-clients' 'vim' 'python-dev' 'guvcview' 'zerofree' 'git' 'subversion' 'git-svn' 'gitg' 'python-pip' 'dkms')
for d in "${dependencies[@]}"; do
  info "Install: $d"
  sudo apt-get -qq -y install "$d"
done
sudo apt-get -qq -y update
sudo apt-get -qq -y upgrade
info "Autostart: lxterminal"
mkdir -p /home/csse3010/.config/autostart
cp /usr/share/applications/lxterminal.desktop autostart/
}

# (2) Python packages
[[ "${steps[2]}" == "y" ]] && {
info "===Python==="
info "Install: mosquitto (mqtt)"
sudo pip -q install mosquitto
}

# (3) OpenCV
[[ "${steps[3]}" == "y" ]] && {
info "===OpenCV==="
version="2.4.8"
mkdir -p "OpenCV"
cd OpenCV
info "1 Removing pre-installed clashing libraries"
sudo apt-get -qq -y remove ffmpeg x264 libx264-dev
info "2 Installing dependenices"
sudo apt-get -qq -y install build-essential checkinstall cmake pkg-config yasm libtiff4-dev libjpeg-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev python-dev python-numpy libtbb-dev libqt4-dev libgtk2.0-dev libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 v4l-utils ffmpeg
sudo apt-get -qq -y install libopencv-dev 
info "3 Downloading OpenCV-$version"
wget -O OpenCV-$version.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/$version/opencv-"$version".zip/download
info "4 Extracting files"
unzip OpenCV-$version.zip
cd opencv-$version
mkdir -p build
cd build
info "5 Preparing cmake build"
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D WITH_TBB=ON -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D BUILD_EXAMPLES=ON -D WITH_QT=ON -D WITH_OPENGL=ON ..
info "6 Compiling C/C++"
make -j2
info "7 Installing OpenCV"
sudo make install
sudo sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig
cd ../..
info "OpenCV-$version installed"
}

# (4) Grub config
[[ "${steps[4]}" == "y" ]] && {
info "===Grub Config==="
info "Edit: /etc/default/grub"
sed -i 's/^GRUB_HIDDEN_TIMEOUT=.*$/#GRUB_HIDDEN_TIMEOUT=3/g' /etc/default/grub
sed -i 's/^GRUB_HIDDEN_TIMEOUT_QUIET=.*$/#GRUB_HIDDEN_TIMEOUT_QUIET=false/g' /etc/default/grub
sed -i 's/^GRUB_TIMEOUT=.*$/GRUB_TIMEOUT=0/g' /etc/default/grub
sudo update-grub

# (6) PringleCV
[[ "${steps[6]}" == "y" ]] && {
cd /home/csse3010
repo=https://github.com/CPonty/PringleCV.git
git clone "$repo" || echo "[ERROR] Git checkout failed"
}

# (7) Git/SVN Setup
[[ "${steps[7]}" == "y" ]] && {
}

# (*) Done
info "===Done==="
info "Size of partition: $(df -h .)"
info "Size of OpenCV: $(du -sh /home/csse3010/OpenCV)"
info ""
info "Installation finished." 
info "Reboot required to finish some upgrades"
info "Install the VBox guest additions / VMWare tools after reboot"

# (8) Reboot
[[ "${steps[8]}" == "y" ]] && {
sudo shutdown -h now
}
