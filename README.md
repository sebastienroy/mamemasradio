# Mamema's radio
The description of how to build a web radio receiver

## History

During the hollidays of my children, I've asked my mother, the grandmother of my children, to babysit them. During this period, my children often listen to FIP radio (www.fip.fr) on the FM. My mother really liked to listen to this radio. Unfortunately, when she was back to home, she couldn't listen to it any more because the FM station is not vailable where she lives (in the north of Alsace, France).
This gave me an idea of Christmas present : I decided to build a radio receiver. Instead of receiving the radio stream from FM, the receiver will get it from web. A quick tour on some web stores shown me that webradio receiver are available for purchasing, however the receiver I wanted for my mother had to meet the following two requirements :
* To be very easy to use, having an ergonomy very close to a traditional FM radio receiver
* Being highly customisable (and customized), in order to help her, each time she listens to the radio, to have a though for her children and grandchildren.

In Alsace, where she lives, the word for "Grandmother" is "Mamema". This is the word my children use for her, and so this is the name I used for this radio receiver.

## General design
### Hardware
* Raspberry Pi Zero W
* Soundcard : Hifiberry DAC+ Zero, or Hifiberry Miniamp
* Man-Machine interface elements : LCD display, rotary encoder, power button
* Interface pcb : a way to make electrical links from the Raspberry GPIO ports and the interface elements
* Casing.
### Software
* Radio stream player
* interface "glue"
