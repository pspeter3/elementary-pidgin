#!/bin/bash 

HOMEUSER=$(echo ~ | awk -F'/' '{ print $1 $2 $3 }' | sed 's/home//g') 
SCRIPTSDIR="/home/$HOMEUSER/.scripts" 
sudo add-apt-repository ppa:webkit-team/ppa
sudo apt-get update 
sudo apt-get upgrade 
sudo apt-get install -y --force-yes pidgin libnotify-bin pidgin-dev libpurple-dev libwebkit-dev bzr checkinstall 
bzr branch lp:~pdffs/pidgin-webkit/karmic-fixes 
cd ./karmic-fixes/ 
make 
sudo checkinstall --fstrans=no --install=yes --pkgname=pidgin-adium --pkgversion "0.1" --default 
cd .. 
sudo rm -r ./karmic-fixes/ 
mkdir -p /home/$HOMEUSER/.scripts/ 
sleep 2; 
cd $SCRIPTSDIR/ 
sleep 2; 
wget http://webupd8.googlecode.com/files/pidgin_adium.sh; 
chmod +x $SCRIPTSDIR/pidgin_adium.sh; 
gconftool-2 -t string -s /desktop/gnome/url-handlers/adiumxtra/command "$SCRIPTSDIR/pidgin-adium.sh %s" 
gconftool-2 -t bool -s /desktop/gnome/url-handlers/adiumxtra/enabled true 
gconftool-2 -t bool -s /desktop/gnome/url-handlers/adiumxtra/needs_terminal false 
sudo chown $HOMEUSER -R /home/$HOMEUSER/.purple/ 
cd /home/$HOMEUSER/.purple/message_styles 
wget http://www.adiumxtras.com/download/2160 
unzip /home/$HOMEUSER/.purple/message_styles/2160 
sudo rm /home/$HOMEUSER/.purple/message_styles/2160
