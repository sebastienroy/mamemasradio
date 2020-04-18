#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 17:45:12 2020

@author: pi
"""


import subprocess
import logging
import datetime

from radiostate import RadioState
from radioevents import StationButtonEvent, PowerButtonEvent
from encoder import EncoderEvent
from powerbutton import PowerEvent
from scrollingtext import ScrollingText
from radioevents import TextUpdateEvent, TextFieldType


class SleepState(RadioState):
    """ This state is active when the radio is switched off.
        Nothing is played, the lcd background light is off
        and a sleeping msg is displayed
    """

    def _get_time_text(self):
        dtg = datetime.datetime.today()
        return dtg.strftime(self._ctxt.rsc.sleep_clock_format)

    def _time_callback(self, originator, value):
        self.logger.debug("_time_callback called")
        self._ctxt.event_queue.put(TextUpdateEvent(value, TextFieldType.SLEEP_CLOCK))


    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        self.logger = logging.getLogger(type(self).__name__)
        self.encoder_pressed = False
        self._clock_rolling_text = ScrollingText(self._get_time_text,
                                                 self._time_callback,
                                                 display_size=20,
                                                 refresh_rate=1)
        self._clock_rolling_text.start()
        self._clock_rolling_text.pause()

    def enter_state(self):
        self.logger.debug("Entering state")
        self._ctxt.lcd.clear()
        self._ctxt.lcd.backlight_enabled = False
        self._ip_displayed = False
        self.encoder_pressed = False
        lines = []
        lines = self._ctxt.rsc.sleep_lines
        for i, line in enumerate(lines):
            if i < 3:
                self._ctxt.lcd.cursor_pos = (i + 1, 0)
                self._ctxt.lcd.write_string(line.ljust(20))
        self._clock_rolling_text.resume()

    def leav_state(self):
        self._clock_rolling_text.pause()

    def handle_event(self, event):
        self.logger.debug("SleepSate handle event : %s", event)
        if type(event) is StationButtonEvent:
            if event.value == EncoderEvent.SWITCH_PRESSED:
                self._ip_displayed = not self._ip_displayed
                self.display_ip()
                self.encoder_pressed = True
            elif event.value == EncoderEvent.SWITCH_RELEASED:
                 self.encoder_pressed = False
        elif type(event) is PowerButtonEvent and event.value == PowerEvent.SWITCH_PRESSED:
            if self.encoder_pressed:
                self._owner.enter_choose_essid()
            else:
                self._owner.switch_radio(True)
        elif type(event) is TextUpdateEvent and event.originator == TextFieldType.SLEEP_CLOCK:
            self.logger.debug("writing clock string : %s", event.value)
            self._ctxt.lcd.cursor_pos = (0, 0)
            self._ctxt.lcd.write_string(event.value.rjust(20))


    def display_ip(self):
        ip = ""
        if self._ip_displayed:
            proc = subprocess.Popen(["hostname", "-I"],
                                    stdout=subprocess.PIPE, universal_newlines=True)
            out, err = proc.communicate()
            ip = "IP : {}".format(out).ljust(20)
        else:
            ip = "".ljust(20)
        self._ctxt.lcd.cursor_pos=(0, 0)
        self._ctxt.lcd.write_string(ip)

    def cleanup(self):
        self.logger.debug("SleepState cleaned up")
        self._clock_rolling_text.stop()
