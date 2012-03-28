#!/bin/bash 
#root access
pass=`zenity --title="Install elementary helper and icons" --width=310 --height=100 --entry --hide-text --text="Insert Root Password:"`
#backup
echo $pass | sudo -S cp -R /usr/share/pixmaps/pidgin/status/16 /usr/share/pixmaps/pidgin/status/16.original
echo $pass | sudo -S cp -R /usr/share/pixmaps/pidgin/status/48 /usr/share/pixmaps/pidgin/status/48.original
#Icons
echo $pass | sudo -S cp -r icons/16/* /usr/share/pixmaps/pidgin/status/16/
echo $pass | sudo -S cp -r icons/48/* /usr/share/pixmaps/pidgin/status/48/
#Script
echo $pass | sudo -S cp -r pidgin_control.py /usr/share/dockmanager/scripts/
#Remove png
cd /usr/share/pixmaps/pidgin/status/48/ && sudo -S rm -R available.png away.png busy.png extended-away.png invisible.png offline.png
killall docky && docky
exit 0
