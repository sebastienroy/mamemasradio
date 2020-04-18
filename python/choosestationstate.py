#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 15:12:37 2018

@author: Sebastien Roy
"""

from threading import Timer
import time

from radiostate import RadioState
from radioevents import StationButtonEvent, ChooseTimeoutEvent
from encoder import EncoderEvent
from resources import Resources

def timeout_callback(event_queue):
    event = ChooseTimeoutEvent()
    event_queue.put(event)

class ChooseStationState(RadioState):
    def __init__(self, ctxt, owner):
        RadioState.__init__(self, ctxt, owner)
        self.target_nb = 0
        self.playlist = self._ctxt.rsc.playlist
        self._timeout = None

    def enter_state(self):
        pre = self._ctxt.rsc.get_i18n(Resources.CHANGE_STATION_ENTRY)
        post = self._ctxt.rsc.get_i18n(Resources.CONFIRM_CHANGE_ENTRY)

        self._ctxt.lcd.cursor_pos = (1, 0)
        self._ctxt.lcd.write_string(pre.ljust(20))
        self.display_target()
        self._ctxt.lcd.cursor_pos = (3, 0)
        self._ctxt.lcd.write_string(post.ljust(20))
        self._reset_timer()
        return

    def handle_event(self, event):
        if type(event) is StationButtonEvent:
            if event.value == EncoderEvent.SWITCH_PRESSED:
                self._timeout.cancel()
                self._owner.enter_choosing(False, self.target_nb)
            elif event.value == EncoderEvent.CW_ROTATION:
                self.target_nb += 1
                self.display_target()
                self._reset_timer()
            elif event.value == EncoderEvent.CCW_ROTATION:
                self.target_nb -= 1
                self.display_target()
                self._reset_timer()
        return

    def _reset_timer(self):
        if self._timeout is not None:
            self._timeout.cancel()
        self._timeout = Timer(self._ctxt.rsc.choose_timeout,
                              timeout_callback,
                              args=[self._ctxt.event_queue])
        self._timeout.start()


    def display_target(self):
        if self.target_nb < 1:
            self.target_nb = len(self.playlist)
        elif self.target_nb > len(self.playlist):
            self.target_nb = 1
        name, url = self.playlist[self.target_nb - 1]
        new_station = "{}: {}".format(self.target_nb, name)
        if len(new_station) > 20:
            new_station = new_station[:20]
        self._ctxt.lcd.cursor_pos = (2, 0)
        self._ctxt.lcd.write_string(new_station.ljust(20))

def _test_fc():
    print("Test fc called")

if __name__ == "__main__":
    timer = Timer(2, _test_fc)
    timer.start()
    time.sleep(5)