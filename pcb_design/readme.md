# Mamema's radio pcb design
This directory contains the design document describing the pcb design of the webradio.

The pcb consists in a main interface pcb and some accessories pcb
## Purpose of the pcb
The Mamema's radio hardware consists in the following components
* A Raspberry pi zero W nano computer
* A sound card (hifiberry miniamp, or DAC+ zero)
* A power button
* A 4x20 LCD display
* 1 or 2 rotary encoders

All these elements are driven from the Raspberry pi GPIO connector. However, because the soundcard is blugged as a hat onto the GPIO port, if the sound courd is plugged directly on the GPIO port, the port would not be available for other physical components.
The idea is then to insert a PCB between the raspberry pi and the sound card, so that the sound card can have access to needed pins, and the remaining free pins are available for the other physical components.

## Manufacturing
Main PCB and accessories PCB may be manufactured directly using these links :
* Main PCB :
https://aisler.net/p/ENDPOVDQ
* Accessories PCB :
https://aisler.net/p/QHNAFNPG

The design has been made using Fritzing 0.9.3b.
Unfortunately, Fritzing org currently asks people for paying to download the software, witch was not the case when Mamema's radio design was made.
If you don't want to pay, you can still compile the sources by yourself.

## Design documents

* webradio_pcb.fzz document describes the main pcb of the web radio. It is used to connect the raspberry pi zero w component to a power button, a rotary encoder used to change the radio station, and optionnaly to another rotary encoder that can be used to change the volume.
* accessories_pcb.fzz document describes accessories pcb. The described pcb has to be cut into 6 parts : 4 rotary encoder pcb and 2 power button pcb. So, parts described by this document can be used for the build of 2 web radios.

The connection between the main pcb and the accessories pcb use F2510-4P connectors. The male F2510-4P headers are soldered on the main pcbs, male dupont headers are soldered on the accessories pcb.
Wires are used between them.
The female headers are used from the main pcb to the accessories pcb.
