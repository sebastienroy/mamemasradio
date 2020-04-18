#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 16:46:44 2018

@author: Sebastien ROY
"""

import subprocess
from threading import Timer
import logging


from radiostate import RadioState
from radioevents import VolumeTimeoutEvent, VolumeButtonEvent
from encoder import EncoderEvent
from resources import Resources



def timeout_callback(event_queue):
    event = VolumeTimeoutEvent()
    event_queue.put(event)


class VolumeState(RadioState):
    def __init__(self, ctxt, owner):
        RadioState.__init__(self, ctxt, owner)
        self.logger = logging.getLogger(type(self).__name__)
        # Timeout thread
        self._timeout = None
        self._timeout_value = ctxt.rsc.volume_timeout
        self._increment = ctxt.rsc.volume_increment
        # initialize volume from mpc
        try:
            proc = subprocess.Popen(["mpc", "volume"],
                                    stdout=subprocess.PIPE,
                                    universal_newlines=True)
            out, err = proc.communicate()
            self._volume = int(out.split(":")[1].strip().strip("%"))
        except:
            self._volume = 20


    def enter_state(self):
        self.logger.debug("Entering state")
        self.display_volume()
        self._reset_timer()
        return

    def leave_state(self):
        self.logger.debug("Leaving state")
        return

    def handle_event(self, event):
        if type(event) is VolumeButtonEvent:
            self.increment(event.value)
            self.display_volume()
            self._reset_timer()
        return

    def display_volume(self):
        # line 2 is empty
        self._ctxt.lcd.cursor_pos = (2, 0)
        self._ctxt.lcd.write_string(" ".ljust(20))
        # line 3 is volume
        msg = self._ctxt.rsc.get_i18n(Resources.VOLUME_MSG_ENTRY)
        self._ctxt.lcd.cursor_pos = (3, 0)
        self._ctxt.lcd.write_string(msg.format(int(self._volume)).ljust(20))
        return

    def increment(self, value):
        # increment or decrement
        if value == EncoderEvent.CCW_ROTATION :
            self._volume -= self._increment
        elif value == EncoderEvent.CW_ROTATION:
            self._volume += self._increment
        # correction if out of bounds
        if self._volume < 0:
            self._volume = 0
        elif self._volume > 100:
            self._volume = 100
        # modify system volume
        self.set_volume()


    def set_volume(self):
        vol = int(self._volume)
        self.logger.debug("Setting volume : %s %s %s", "mpc", "volume", str(vol))
        subprocess.call(["mpc", "volume", str(vol)])
        return

    def _reset_timer(self):
        if self._timeout is not None:
            self._timeout.cancel()
        self._timeout = Timer(self._timeout_value,
                              timeout_callback,
                              args=[self._ctxt.event_queue])
        self._timeout.start()

