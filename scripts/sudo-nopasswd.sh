#!/bin/bash
if [ -z "$1" ]; then
  echo "[INFO] Run visudo with script as first parameter"
  export EDITOR=$0 && sudo -E visudo
else
  echo "[INFO] Modifying /etc/sudoers"
  sed -i '/#Override individual users/ d' $1
  sed -i $'/csse3010\t/ d' $1
  echo -e "#Override individual users" >> $1
  echo -e "csse3010\tALL=NOPASSWD: ALL" >> $1
fi
