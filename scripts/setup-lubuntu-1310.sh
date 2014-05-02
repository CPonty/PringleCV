#!/bin/bash
# Script to install PringleCV dependencies & tools for CSSE3010 on a Lubuntu 13.X VM.
#
# Download & run script: 
#   file=setup-lubuntu-1310.sh
#   url=http://bit.ly/1o8oe5O
#   wget -O $file $url
#   chmod +x $file
#   ./$file
#
# OpenCV on Ubuntu: http://help.ubuntu.com/community/OpenCV

#      1 2 3 4 5 6 7 8 9
steps=(y y y y y y y y n)
#------------------------------------------------------------------------------------
info () { echo "[INFO] $1"; }
cd /home/csse3010

# (1) Update/upgrade current packages
[[ "${steps[0]}" == "y" ]] && {
info "===Update/Upgrade==="
sudo apt-get -y update
#sudo apt-get -y upgrade <-- evil!
}

# (2) Basic Packages
[[ "${steps[1]}" == "y" ]] && {
info "===Basic Packages==="
dependencies=('mosquitto' 'mosquitto-clients' 'vim' 'python-dev' 'guvcview' 'zerofree' 'git' 'subversion' 'git-svn' 'gitg' 'python-pip' 'dkms')
for d in "${dependencies[@]}"; do
  info "Install: $d"
  sudo apt-get -qq -y install "$d"
done
[[ -z "$(grep 'set background=' /home/csse3010/.vimrc )" ]] && \
  echo "set background=dark" >> /home/csse3010/.vimrc
}

# (3) Lxterminal Autostart
[[ "${steps[2]}" == "y" ]] && {
info "===LXTerminal Autostart==="
autodir=/home/csse3010/.config/autostart
mkdir -p "$autodir"
cp /usr/share/applications/lxterminal.desktop "$autodir"
}

# (4) Python packages
[[ "${steps[3]}" == "y" ]] && {
info "===Python==="
info "Install: mosquitto (mqtt)"
sudo pip -q install mosquitto
}

# (5) OpenCV
[[ "${steps[4]}" == "y" && ! -d /home/csse3010/OpenCV ]] && {
info "===OpenCV==="
version="2.4.8"
cd /home/csse3010
mkdir -p OpenCV
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
cd ..
info "8 Remove precompiled headers (~1.5GB"
find . -type f -name "*.gch" -exec rm -f {} \;
cd ..
info "OpenCV-$version installed"
info "Size of partition: $(df -h .)"
info "Size of OpenCV: $(du -sh /home/csse3010/OpenCV)"
}

# (6) Grub config
[[ "${steps[5]}" == "y" ]] && {
info "===Grub Config==="
info "Edit: /etc/default/grub"
sudo sed -i 's/^GRUB_HIDDEN_TIMEOUT=.*$/#GRUB_HIDDEN_TIMEOUT=3/g' /etc/default/grub
sudo sed -i 's/^GRUB_HIDDEN_TIMEOUT_QUIET=.*$/#GRUB_HIDDEN_TIMEOUT_QUIET=false/g' /etc/default/grub
sudo sed -i 's/^GRUB_TIMEOUT=.*$/GRUB_TIMEOUT=0/g' /etc/default/grub
sudo update-grub
}

# (7) PringleCV
[[ "${steps[6]}" == "y" && ! -d /home/csse3010/PringleCV ]] && {
cd /home/csse3010
repo=https://github.com/CPonty/PringleCV.git
git clone "$repo" || echo "[ERROR] Git checkout failed"
}

# (8) Git/SVN Setup
[[ "${steps[7]}" == "y" ]] && {
cd /home/csse3010
cp PringleCV/scripts/git-svn-setup.sh .
chmod +x git-svn-setup.sh
}

# (*) Done
info "===Done==="
info ""
info "Installation finished." 
info "Reboot required to finish some upgrades"
info "Install the VBox guest additions / VMWare tools after reboot"

# (9) Reboot
[[ "${steps[8]}" == "y" ]] && {
sudo reboot now
}
