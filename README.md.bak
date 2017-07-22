# RadioPlayer 
Simple Radio/Spotify Player for OrangePi Zero 

###### Install OS and basic setup
Install armbian and logon to SSH

Install the basic

**Pip**
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
```

**More basic setup**
```
sudo apt-get install python-dev python-pip libfreetype6-dev libjpeg-dev
sudo apt-get purge python-pip
sudo pip install requests
```

***OLED driver***
```
sudo -H pip install --upgrade luma.oled
```
***GPIO library***
```
git clone git@github.com:duxingkei33/orangepi_PC_gpio_pyH3.git
cd orangepi_PC_gpio_pyH3
sudo python setup.py  install
```

***Install Spotify-Connect-Web***
```
apt-get install avahi-utils
sudo nano /etc/systemd/system/spotify-avahi.service
```
Insert the following:
```
[Unit]
Description=Spotify Connect Zeroconf
After=network.target

[Service]
User=root
ExecStart=/usr/bin/avahi-publish-service orange _spotify-connect._tcp 4000 VERSION=1.0 CPath=/login/_zeroconf
Restart=always
RestartSec=10
StartLimitInterval=30
StartLimitBurst=20

[Install]
WantedBy=multi-user.target
```
Auto start up
```
systemctl enable spotify-avahi.service
```

Now install Spotify-Connect-Web
```
cd
mkdir /install
cd /install
wget https://github.com/Fornoth/spotify-connect-web/releases/download/0.0.3-alpha/spotify-connect-web_0.0.3-alpha.tar.gz

tar zxvf spotify-connect-web_0.0.3-alpha.tar.gz
cp <Your keyFile> /install/spotify-connect-web

sudo nano /etc/systemd/system/spotify-connect.service
```
Now insert the folloing:
```

[Unit]
Description=Spotify Connect
After=network.target

[Service]
User=root
WorkingDirectory=/install/spotify-connect-web/
ExecStart=/install/spotify-connect-web/spotify-connect-web --bitrate 320 --name Stuen --username <username> --password <password> --playback_device hw:CARD=audiocodec,DEV=0
Restart=always
RestartSec=10
StartLimitInterval=30
StartLimitBurst=20

[Install]
WantedBy=multi-user.target

```
Enable autostart
```
systemctl enable spotify-connect.service
```

***Install the player script***
```
cd 
mkdir script
cd script
git clone xxxx .
sudo nano /etc/rc.local
```

Insert this before exit
```
for i in 3 2 1; do echo 0 >/sys/devices/system/cpu/cpu${i}/online; done # h3consumption

cd /root/script
sudo python radio.py > /dev/null 2>&1 &
```


***Credit***
https://github.com/thk4711/orangepi-radio

 