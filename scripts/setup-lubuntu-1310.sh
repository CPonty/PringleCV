#!/bin/bash
# Script to install PringleCV dependencies & tools for CSSE3010 on a Lubuntu 13.X VM.

#      1 2 3 4 5 6 7 8 9 10
steps=(y y y y y y y y y y)
# (1) Update/upgrade current packages
# (2) Add Packages
# (3) .vimrc, .bashrc
# (4) Lxterminal autostart at login
# (5) Python packages
# (6) OpenCV
# (7) Grub config - open on startup
# (8) Download PringleCV
# (9) Git/SVN Setup
# (10) Sudo: set nopasswd for user
#------------------------------------------------------------------------------

info () { echo "[INFO] $1"; }
lineSpam () { printf "\n%.0s" {1..100}; }

loadScript () {
  #download this script
  file=setup-lubuntu-1310.sh
  url=http://bit.ly/1o8oe5O
  wget -O $file $url
  chmod +x $file
}

cd $HOME

# (1) Update/upgrade current packages
[[ "${steps[0]}" == "y" ]] && {
info "===Update/Upgrade==="
sudo apt-get -y update
sudo apt-get -y upgrade
}

# (2) Add Packages
#     zerofree: utility for zeroing free memory blocks via grub
#       run & clone the VM to minimize disk filesize
#     dkms: install before virtualbox guest additions to avoid problems
[[ "${steps[1]}" == "y" ]] && {
info "===Basic Packages==="
packages=('mosquitto' 'mosquitto-clients' 'vim' 'python-dev' 'guvcview' 'zerofree' 'git' 'subversion' 'git-svn' 'gitg' 'python-pip' 'dkms')
for p in "${packages[@]}"; do
  info "Install: $p"
  sudo apt-get -qq -y install "$p"
done
}

# (3) .vimrc, .bashrc
#     alias sudo='sudo ' allows other aliases to work when prefixed by sudo 
[[ "${steps[2]}" == "y" ]] && {
info "===Update .vimrc==="
vimlines=("set background=dark")
for l in "${vimlines[@]}"; do
  [[ -z `grep "$(cut -d'=' -f1 <<< "$l")=" $HOME/.vimrc` ]] && {
    info "$l"
    echo "$l" >> $HOME/.vimrc
  } || {
    info "Skip: $l"
  }
done
info "===Update .bashrc==="
aliases=("alias sudo='sudo '" "alias vi='vim'" "alias down='sudo shutdown -h now'" "alias reboot='shutdown -h'")
for a in "${aliases[@]}"; do
  [[ -z `grep "$(cut -d'=' -f1 <<< "$a")=" $HOME/.bashrc` ]] && {
    info "$a"
    echo "$a" >> $HOME/.bashrc
  } || {
    info "Skip: $a"
  }
done
}

# (4) Lxterminal autostart at login
[[ "${steps[3]}" == "y" ]] && {
info "===LXTerminal Autostart==="
autodir=$HOME/.config/autostart
mkdir -p $autodir && cd $autodir
info "Add: ~/.config/autostart/lxterminal.desktop"
cp /usr/share/applications/lxterminal.desktop .
sed -i 's/^disable_autostart=.*$/disable_autostart=no/g' \
  $HOME/.config/lxsession/Lubuntu/desktop.conf && \
  info "disable_autostart=no"
}

# (5) Python packages
[[ "${steps[4]}" == "y" ]] && {
info "===Python==="
info "Install: mosquitto (mqtt)"
sudo pip -q install mosquitto
}

# (6) OpenCV
#     OpenCV on Ubuntu: http://help.ubuntu.com/community/OpenCV
[[ "${steps[5]}" == "y" && ! -d $HOME/OpenCV ]] && {
info "===OpenCV==="
version="2.4.8"
cvdir=$HOME/OpenCV
mkdir -p $cvdir && cd $cvdir
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
info "8 Remove precompiled headers (~1.5GB)"
find . -type f -name "*.gch" -exec rm -f {} \;
cd ..
info "OpenCV-$version installed"
info "Size of partition: $(df -h .)"
info "Size of OpenCV: $(du -sh $HOME/OpenCV)"
}
[[ "${steps[5]}" == "y" && -d $HOME/OpenCV ]] && {
  info "Skip - $HOME/OpenCV exists"
}

# (7) Grub config - open on startup
[[ "${steps[6]}" == "y" ]] && {
info "===Grub Config==="
grubfile=/etc/default/grub
info "Edit: $grubfile"
sudo sed -i 's/^GRUB_HIDDEN_TIMEOUT=.*$/#GRUB_HIDDEN_TIMEOUT=3/g' $grubfile
sudo sed -i 's/^GRUB_HIDDEN_TIMEOUT_QUIET=.*$/#GRUB_HIDDEN_TIMEOUT_QUIET=false/g' $grubfile
sudo sed -i 's/^GRUB_TIMEOUT=.*$/GRUB_TIMEOUT=10/g' $grubfile
sudo update-grub
}

# (8) Clone PringleCV
info "===PringleCV==="
[[ "${steps[7]}" == "y" && ! -d $HOME/PringleCV ]] && {
cd $HOME
repo=https://github.com/CPonty/PringleCV.git
git clone "$repo" || echo "[ERROR] Git checkout failed"
}
[[ "${steps[7]}" == "y" && -d $HOME/PringleCV ]] && {
  info "Skip - $HOME/PringleCV exists"
}

# (9) Git/SVN Setup
[[ "${steps[8]}" == "y" ]] && {
info "===git-svn-setup==="
docdir=$HOME/Documents
mkdir -p $docdir && cd $docdir
cp $HOME/PringleCV/scripts/git-svn-setup.sh . && chmod +x git-svn-setup.sh
cd $HOME
svn co https://source.eait.uq.edu.au/svn/csse3010/trunk np2_svn \
--username csse3010@svn.itee.uq.edu.au --password csse3010 <<< "
no
"
}

# (10) Sudo: set nopasswd for user
[[ "${steps[9]}" == "y" ]] && {
echo "===Sudo nopasswd==="
file=$HOME/PringleCV/scripts/sudo-nopasswd.sh
chmod +x $file && $file
}

# (*) Done
info "===Done==="
info ""
info "Installation finished." 
info "Reboot required to finish some upgrades"
info "Install the VBox guest additions / VMWare tools after reboot"
