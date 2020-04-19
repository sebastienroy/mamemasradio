
# Mamema's radio user manual
## Introduction
This manual describes the administration actions of the Mamema's webradio
1. Wifi setup (alternative method)
2. Access to the configuration file
3. Modifications of the configuration file
## 1. Wifi setup (alternative method)
Unlike otherwise specified, the login/password of the user is pi/raspberry
## 2. Access to the configuration file
### 1. Using ftp client
### 2. Using ssh
## 3. Modification of the configuration file
### Random_messages
### Dated messages
### Playlist
### Misc
There is a few additional thing you can freely configure. Be careful to not put the mess in the configuration.
1. The clock format may be modified in order for instance to display the date/time in a more complete maner. The format is defined in the configuration file using the [clock]/format entry. The format definition may be found [here](https://strftime.org/). Be carefull to not exceed 20 characters.

## Reference
[Mamema's radio development site](https://github.com/sebastienroy/mamemasradio)
