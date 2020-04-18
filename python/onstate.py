#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 20:02:03 2018

@author: Sebastien Roy
"""

import random
import subprocess
import logging

import RPi.GPIO as GPIO

from playingstate import PlayingState
from choosestationstate import ChooseStationState
from volumestate import VolumeState
from powerbutton import PowerEvent
from radiostate import RadioState
from radioevents import ChooseTimeoutEvent, PowerButtonEvent, VolumeButtonEvent, VolumeTimeoutEvent


class OnState(RadioState):
    """ This class handle one of the power state of the radio : the "on" state
    """
    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        self.logger = logging.getLogger(type(self).__name__)
        self._track_nb = 1
        self._playing_state = PlayingState(self._ctxt, self._track_nb, self)
        self._choosing_state = ChooseStationState(self._ctxt, self)
        self._volume_state = VolumeState(self._ctxt, self)
        self._sub_state = None

    def enter_state(self):
        self.logger.debug("Entering state")
        random_msg = self._ctxt.rsc.today_msg
        if not random_msg:
            random_msg = random.choice(self._ctxt.rsc.random_msgs)
        self._playing_state.random_msg = random_msg
        self._sub_state = self._playing_state

        self._ctxt.lcd.clear()
        self._ctxt.lcd.backlight_enabled = True
        self._ctxt.power_button.led = True
        self._ctxt.wifi_thread.resume()

        # switch on the soundcard
        mute_gpio = self._ctxt.rsc.mute_gpio
        if mute_gpio != 0:
            GPIO.output(mute_gpio, GPIO.HIGH)

        subprocess.call(["mpc", "play", str(self._track_nb)])

        self._sub_state.enter_state()

    def leave_state(self):
        self.logger.debug("Leaving state")
        self._ctxt.wifi_thread.pause()
        self._sub_state.leave_state()

    def handle_event(self, event):
        if type(event) is PowerButtonEvent and event.value == PowerEvent.SWITCH_PRESSED:
            self._owner.switch_radio(False)
        elif type(event) is ChooseTimeoutEvent:
            self.enter_choosing(False)
        elif type(event) is VolumeTimeoutEvent:
            self.leave_volume()
        elif type(event) is VolumeButtonEvent:
            self.change_volume(event)
        elif self._sub_state is not None:
            self._sub_state.handle_event(event)

    def leave_volume(self):
        if self._sub_state == self._volume_state:
            self._sub_state.leave_state()
            self._sub_state = self._playing_state
            self._sub_state.enter_state()

    def change_volume(self, event):
        if self._sub_state == self._volume_state:
            self._sub_state.handle_event(event)
        else:
            self._volume_state.increment(event.value)
            self._sub_state.leave_state()
            self._sub_state = self._volume_state
            self._sub_state.enter_state()

    def enter_choosing(self, status, track_nb=0):
        """ switches on/off the choosing status, depending on status parameter
        """
        self._sub_state.leave_state()
        if status:
            if track_nb < 1:
                track_nb = len(self._ctxt.rsc.playlist)
            elif track_nb > len(self._ctxt.rsc.playlist):
                track_nb = 1
            self._choosing_state.target_nb = track_nb
            self._sub_state = self._choosing_state
        else:
            if track_nb != 0:
                self._track_nb = track_nb
                self._playing_state.track_nb = track_nb
                subprocess.call(["mpc", "play", str(self._track_nb)])
            self._sub_state = self._playing_state
        self._sub_state.enter_state()

    def cleanup(self):
        self._playing_state.cleanup()
        self._choosing_state.cleanup()
        self._volume_state.cleanup()