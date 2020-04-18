#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 20:38:09 2018

@author: sebastien.roy
"""

import RPi.GPIO as GPIO
from enum import Enum
import time

class EncoderEvent(Enum) :
    CW_ROTATION = +1
    CCW_ROTATION = -1
    SWITCH_PRESSED = 2
    SWITCH_RELEASED = 3


class RotaryEncoder(object):

    def __init__(self, pina, pinb, switch, callback):   # The callback expected signature
        """Initialisation of the Rotary encoder

        Parametres :
            pina -- GPIO number of the A pin of the rotary encoder
            pinb -- GPIO number of the A pin of the rotary encoder
            switch -- GPIO number of the switch of the rotary encoder.
                If 0, the rotary encoder has no switch or the switch is not connected
            callback -- a reference to a callback function. The function signature is the following
                1st argument : the originator (will be the RotaryEncoder instance)
                2nd argument : the EncoderEvent that initiated the callback
        """
        self._pina = pina
        self._pinb = pinb
        self._switch = switch
        self._rot_value = 0
        self._last_rest_value = 0
        self._callback = callback

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._pina, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._pinb, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(self._pina, GPIO.RISING, callback=self._rotation_callback)    # No bounce time
        GPIO.add_event_detect(self._pinb, GPIO.RISING, callback=self._rotation_callback)    # No bounce time
        if switch != 0 :
            GPIO.setup(self._switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(self._switch, GPIO.BOTH, callback=self._switch_callback, bouncetime=5)

        self._pina_value = GPIO.input(pina)
        self._pinb_value = GPIO.input(pinb)
        return

    def _rotation_callback(self, pin):
        a_value = GPIO.input(self._pina)
        b_value = GPIO.input(self._pinb)
        if a_value == self._pina_value and b_value == self._pinb_value:    # Same interrupt as before (Bouncing)?
            return                                                         # ignore interrupt!

        self._pina_value = a_value                                          # remember new state
        self._pinb_value = b_value                                          # for next bouncing check
        if (a_value and b_value):                               # Both one active? Yes -> end of sequence
            if pin == self._pinb:                           # Turning direction depends on
                self._callback(self, EncoderEvent.CW_ROTATION)    # which input gave last interrupt
            else:                                                       # so depending on direction either
                self._callback(self, EncoderEvent.CCW_ROTATION)    # increase or decrease counter
        return                                                      # THAT'S IT

    def _switch_callback(self, pin):
        time.sleep(0.01)  # let edge time to stabilise before reading value
        event = EncoderEvent.SWITCH_PRESSED if GPIO.input(pin) == 0 else EncoderEvent.SWITCH_RELEASED
        self._callback(self, event)
        return

    def __repr__(self):
        return "Rotary Encoder : Pin_a = {pina}, Pin_b = {pinb}, switch = {switch}".format( \
                pina=self._pina, pinb=self._pinb, switch=self._switch)

    def __del__(self):
        self.clear()
        return

    def clear(self):
        GPIO.remove_event_detect(self._pina)
        GPIO.remove_event_detect(self._pinb)
        if self._switch != 0:
            GPIO.remove_event_detect(self._switch)

# tests
def test_callback(originator, event):
    print("Originator : ", originator)
    print("Event : ", event )
    return

if __name__ == "__main__" :
    print("Tests unitaires avec pina = 5, pinb = 6, switch = 4")
    encoder = RotaryEncoder(5,6,4,callback=test_callback)
    input("Press enter to end...")







