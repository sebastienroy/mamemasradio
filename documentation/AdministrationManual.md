
# Mamema's radio administration manual
## Introduction

Mamema's radio is basicaly composed of a raspberry pi computer, a soundcard, some interface components (lcd screen, rotary button, power button), and all the software that make all this working together.
The software is parameterized through a configuration file. The aim of this administration guide is to explain how to access to this configuration file, and wich part can be modified safely.
The audience of this manual is people that are confident with computer configuration.
This manual and other documentation can be found on the Mamema's repository :
http://github.com/sebastienroy/mamemasradio

This manual describes the following administration actions of the Mamema's webradio. 
1. Wifi setup (alternative method)
2. Access to the configuration file
3. Modifications of the configuration file


## 1. Wifi setup (alternative method)
In order to access to the radio streams, but als in order to conduct the administration actions, Mamema's radio needs first to be connected to your wifi network.
The configuration of the wifi network is already described in the user manual. However, for any reason, you may want to configure the network in another maner.
Unlike otherwise configured (we recommand to configure another password and to write it somewhere), the login/password of the user is pi/raspberry.
You can configure the wifi ssid and password of the wifi network by :
1. dismount the rear pannel of the radio
2. connect a keyboard on the usb port of the raspberry pi board
3. connect a screen on the hdmi port of the raspberry pi
4. modify the `wpa_supplicant.conf` file :
 
`sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`

Go to the bottom of the file and add the following:
```
network={
    ssid="yourSSID"
    psk="yourPassword"
}
```
With `yourSSID` and `yourPassword` adapted to your local wifi network
Then reboot :
`sudo reboot`
Your radio should have now access to the wifi network.
You can now disconnect your screen, your keyboard and close the back of the radio case. The rest of the administration actions will be done remotely.

## 2. Access to the configuration file
All the configuration of the radio (list of radios, displayed messages, ...) is defined in a configuration file : 
`/home/pi/webradio.cfg`
You can access to this file through 2 different methods (both actually use the same network protocol)
### 1. Using an ftp client
From another computer, use a ftp client, such as FileZilla to open an ftp session. 
Use the following parameters :
* Protocol : SFTP (SSH File Transfer Protocol)
* Host : mamemasradio, or another name, depending on your local configuration (you can also use the ip address of the radio. When the radio is off, press on the radio station button, the ip address will be displayed)
*  Port : leave empty, 
* User : `pi`
* Password : `raspberry` is the default password, but you may have configured another one.

Once connected, you have access to the configuration file :
`/home/pi/webradio.cfg`
### 2. Using ssh
You can open directly an ssh session from another computer to the radio :
`ssh pi@mamemasradio`
you can modify the configuration file using the following command :
`nano /home/pi/webradio.cfg`
## 3. Modification of the configuration file
In the configuration file, some sections are intended to be modify, and some other not.
The sections that can be modified easily, without any particular risk are  the following :
* Random_messages
* Dated_messages
* Playlist
### Random_messages
In the random message section (that begins with `[random_messages]`), all the entries are messages that will be displayed randomly on the second line of the radio lcd display.
These messages are displayed randomly when there is no message related to the current date in the section `[dated_messages]`
Each entry begins with a labed, followed by a column. This label is not used for the display.
The message can be longuer than the size of the display (20 characters). In this case the message is scrolled automatically.
Exemple :
`1: Hello world!`
### Dated messages
In the section `[dated_messages]`, the configured messages depending on the date (in french format) corresponding to their label.
Example :
`25/12: Merry Christmas!`
This message will only be displayed the 25th of december.
### Playlist
The entries of the `[playlist]`section are the list of the titles and the url of the radio stations. They will appear in the same order as they appear in the configuration file.
There is not limit on the number of configured stations

There is a few additional thing you can freely configure. Be careful to not put the mess in the configuration.
1. Welcome message may be modified in the `[general]` section. Take care to not exceed 16 characters.
2. The clock format may be modified in order for instance to display the date/time in a more complete maner. The format is defined in the configuration file using the [clock]/format entry. The format definition may be found [in the description of the Python strftime function](https://strftime.org/). Be carefull to not exceed 20 characters.

## Reference
[Mamema's radio development site](https://github.com/sebastienroy/mamemasradio)
