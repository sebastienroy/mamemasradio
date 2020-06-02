# Mamema's radio
A web radio receiver with a classical hifi style ergonomy

![Mamema's radio](https://github.com/sebastienroy/mamemasradio/blob/develop/documentation/pictures/radio_front_on_500px.jpg)

## History

During the hollidays of my children, I've asked my mother, the grandmother of my children, to babysit them. During this period, my children were often listening to FIP radio (www.fip.fr) on the FM. My mother really liked listening to this radio. Unfortunately, when she was back to home, she couldn't listen to it any more because the FM station is not vailable where she lives (in the north of Alsace, France).
This gave me an idea of Christmas present : I decided to build a radio receiver. Instead of receiving the radio stream from FM, the receiver will get it from web. A quick tour on some web stores shown me that webradio receiver are available for purchasing, however the receiver I wanted for my mother had to meet the following two requirements :
* To be very easy to use, having an ergonomy very close to a traditional FM radio receiver
* Being highly customisable (and customized), in order to help her, each time she listens to the radio, to have a though for her children and grandchildren.

In Alsace, where she lives, the word for "Grandmother" is "Mamema". This is the word my children use for her, and so this is the name I used for this radio receiver.

## Features
* Plays audio stream through wifi network. No limit for the number of programmable radio stations
* Can also be used as a bluetooth speaker
* Uses classics physical commands : power button, rotary buttons
* Built around a raspberry pi zero low cost - low power consumption nano computer
* Excellent audio quality : uses a high quality sound card.
* Displays personnalisable messages and birthdays reminders : perfect as a present for your family members. No limitation for the length of the message, the text scrolls if wider than the screen
* Can be built as a standalone radio, integrating speakers and an amplifier, or as an audio source for a separated stereo amplifier

## General design
### Hardware
* Raspberry Pi Zero W
* Soundcard :  Hifiberry Miniamp (standalone radio), or Hifiberry DAC+ Zero (audio source for external hifi amplifier)
* Loud speakers (standalone radio)
* Man-Machine interface elements : LCD display, rotary encoder, power button
* Interface pcb and accessories pcb : a way to make electrical links from the Raspberry GPIO ports and the interface elements. To be manufactured by a dedicated factory (links provided)
* Casing.
### Software
* Radio stream player (Music Player Daemon)
* User interactions managed by python software components (specific developments)
* Based on Raspbian operating system
