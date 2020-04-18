#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 20:42:50 2018

@author: Sebastien Roy
"""

from enum import Enum
import RPi.GPIO as GPIO
import time

class PowerEvent(Enum) :
    SWITCH_PRESSED = 0
    SWITCH_RELEASED = 1

class PowerButton:
    def __init__(self, switch_pin, led_pin, callback):
        self._switch_pin = switch_pin
        self._led_pin = led_pin
        self._callback = callback

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._led_pin, GPIO.OUT, initial=GPIO.LOW)

        GPIO.add_event_detect(self._switch_pin, GPIO.BOTH, callback=self._switch_callback, bouncetime=50)
        return

    def _set_callback(self, callback):
        self._callback = callback


    def _switch_callback(self, pin):
        time.sleep(0.01) # let edge time to complete before reading value
        event = PowerEvent.SWITCH_PRESSED if GPIO.input(self._switch_pin) == 0 else PowerEvent.SWITCH_RELEASED
        if self._callback is not None:
            self._callback(self, event)

    def __del__(self):
        GPIO.remove_event_detect(self._switch_pin)

    def clear(self):
        GPIO.remove_event_detect(self._switch_pin)


    def _set_led(self, value):
        state = GPIO.HIGH if value else GPIO.LOW
        GPIO.output(self._led_pin, state)

    led = property(fset=_set_led)
    callback = property(fset=_set_callback)



def my_test_callback(originator, event):
    global status
    print("Callback from : {} ; event : {}".format(originator, event))
    if event == PowerEvent.SWITCH_PRESSED:
        status = not status
        originator.led = status

if __name__ == "__main__":
    status = False
    button = PowerButton(25, 26, my_test_callback)
    print("Clickez sur le power button")
    input("Appuyez sur entree pour quitter")
    del button
    GPIO.cleanup()

