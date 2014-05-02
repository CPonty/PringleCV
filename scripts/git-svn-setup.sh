#!/bin/bash

user=""
while [ "$user" == "" ]; do
  echo "Enter your student username (e.g. s1234567@student.uq.edu.au)"
  read -r user
done
sn=`cut -d'@' -f1 <<< "$user"`
stype=""
echo "[INFO] 1: Undergraduate"
echo "[INFO] 2: Postgraduate (Masters)"
while [[ "$stype" != "1" && "$stype" != "2" ]]; do
  echo -n "Enter your study mode (1 or 2):"
  read -r stype
done

[[ "$stype" == "1" ]] && course="csse3010" || course="csse7301"
path=/home/csse3010/Documents
mkdir -p $path && cd $path
existingFolders="$(find `pwd` -type d -name 'csse3010-s*' -print0)"
[[ ! -z "$existingFolders" ]] && {
  echo -e "[INFO] Student SVN folder(s) already exist:\n  $existingFolders"
  ans=""
  while [[ "$ans" != "y" && "$ans" != "n" ]]; do
    echo -n "Remove folder(s)? (y/n): "
    read -r ans
  done
  if [ "$ans" == "y" ]; then
    echo "[INFO] Removing folder(s)"
    find `pwd` -type d -name 'csse3010-s*' -print0 \
     | xargs --no-run-if-empty -0 rm -r 
  else
    exit 0
  fi
}

echo "[INFO] SVN checkout for user $user, student $sn, course $course"
git svn clone --username $user https://source.eait.uq.edu.au/svn/$course-$sn
echo "[INFO] Repository checked out to ~/Documents/csse3010-$sn"
