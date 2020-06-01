# Mamema's radio pcb design
This directory contains the design document describing the pcb design of the webradio.

The pcb consists in a main interface pcb and some accessories pcb

* Main pcb :

![main pcb schema](https://github.com/sebastienroy/mamemasradio/blob/develop/pcb_design/pictures/mainpcb_thumb.png)

* Accessories pcb :

![accessories pcb schema](https://github.com/sebastienroy/mamemasradio/blob/develop/pcb_design/pictures/accessoriespcb_thumb.png)


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

The accessories board has to be cut into 6 parts : 4 rotary encoder supports, and 2 power button supports. Thus, one accessories board can be used to make two separate Mamema's radios.

The design has been made using Fritzing 0.9.3b.
Unfortunately, Fritzing org currently asks people for paying to download the software, witch was not the case when Mamema's radio design was made.
If you don't want to pay, you can still compile the sources by yourself.

## Design documents

* webradio_pcb.fzz document describes the main pcb of the web radio. It is used to connect the raspberry pi zero w component to an LCD display, a power button, a rotary encoder used to change the radio station, and optionnaly to another rotary encoder that can be used to change the volume. This pcb also holds a logic level converter (in order to convert voltage from 3.3V from the raspberry to 5V for the LCD display) and a resistor needed for the power button LED.
* accessories_pcb.fzz document describes accessories pcb. The described pcb has to be cut into 6 parts as described above. These parts are used as support to connect the rotary encoder and the power button, but they are also used to attach these components on the case of the radio. The power button in particular cannot be attached on the case by itself.

The connection between the main pcb and the accessories pcb use F2510-4P connectors. The male F2510-4P headers are soldered on the main pcbs, male dupont headers are soldered on the accessories pcb.
Wires are used between them.
The female headers are used from the main pcb to the accessories pcb.
