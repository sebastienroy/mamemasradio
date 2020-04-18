#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 14:59:22 2018

@author: Sebastien Roy
"""
from RPLCD.i2c import CharLCD
from resources import Resources
import subprocess
import logging
import datetime

from radioevents import WifiEvent, TextUpdateEvent, TextFieldType, StationButtonEvent
from encoder import EncoderEvent
from scrollingtext import ScrollingText
from radiostate import RadioState

class PlayingState(RadioState):
    """ This class defines the behaviour of the webradio when it is
    on playing state
    """
    def __init__(self, ctxt, track_nb, owner):
        """ Initialisation
        """
        RadioState.__init__(self, ctxt, owner)
        self.logger = logging.getLogger(type(self).__name__)
        self.track_nb = track_nb
        self._lcd = ctxt.lcd
        self._rsc = ctxt.rsc
        self._wifi_level = 0
        self.random_msg = ""
        self._random_msg_display = ScrollingText(self._random_msg, self._random_msg_callback,
                                           display_size=20, refresh_rate=0,
                                           scroll_begin_delay=self._rsc.scroll_begin,
                                           scroll_end_delay=self._rsc.scroll_end,
                                           scroll_rate=self._rsc.scroll_rate)
        self._random_msg_display.pause()
        self._random_msg_display.start()
        # The name of the radio is not updated automatically when setting refresh_rate = 0
        self._name_display = ScrollingText(self._radio_name, self._radio_name_callback,
                                           display_size=20, refresh_rate=0,
                                           scroll_begin_delay=self._rsc.scroll_begin,
                                           scroll_end_delay=self._rsc.scroll_end,
                                           scroll_rate=self._rsc.scroll_rate)
        self._name_display.pause()
        self._name_display.start()
        # The title of the track is updated automatically every 5 seconds
        self._title_display = ScrollingText(self._track_title, self._track_title_callback,
                                            display_size=20, refresh_rate=1,
                                           scroll_begin_delay=self._rsc.scroll_begin,
                                           scroll_end_delay=self._rsc.scroll_end,
                                           scroll_rate=self._rsc.scroll_rate)
        self._title_display.pause()
        self._title_display.start()

    def enter_state(self):
        self.logger.debug("Entering state")
        self._display_welcome()
        self._display_wifi_level()
#        self._display_random_msg()

        self._random_msg_display.resume()
        self._name_display.resume()
        self._title_display.resume()

        return

    def leave_state(self):
        self.logger.debug("Leaving state")
        self._random_msg_display.pause()
        self._name_display.pause()
        self._title_display.pause()

    def _random_msg_callback(self, originator, value):
        self._ctxt.event_queue.put(TextUpdateEvent(value, TextFieldType.RANDOM_MSG))

    def _radio_name_callback(self, originator, value):
        self._ctxt.event_queue.put(TextUpdateEvent(value, TextFieldType.RADIO_NAME))

    def _track_title_callback(self, originator, value):
        self._ctxt.event_queue.put(TextUpdateEvent(value, TextFieldType.TRACK_TITLE))

    def _display_welcome(self):
         msg = self._rsc.welcome_msg.ljust(Resources.WELCOME_MSG_MAX_SIZE)
         self._lcd.cursor_pos = (0, 0)
         self.logger.debug("The welcome message is %s", msg)
         self._lcd.write_string(msg)
         return

    def _display_wifi_level(self):
        msg = "\x00{}/5".format(self._wifi_level) # Assume that the wifi symbol is nb 0
        self._lcd.cursor_pos = (0, 16)
        self._lcd.write_string(msg)
        return

    def _random_msg(self):
        return self.random_msg

    def _radio_name(self):
        self.logger.debug("Radio name computation")
        proc = subprocess.Popen(["mpc", "--format=%name%", "current"],
                                stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        self.logger.debug("Out = %s",out)
        if out.strip():
            name = out.strip()
        else:
            name, url = self._rsc.playlist[self.track_nb - 1]
        return name

    def _track_title(self):
        proc = subprocess.Popen(["mpc", "--format=%title%", "current"],
                                stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        title = out.strip()
        if len(title) > 0:
            return title
        else:
            dtg = datetime.datetime.today()
            return dtg.strftime(self._ctxt.rsc.clock_format).rjust(20)

    def handle_event(self, event):
        if type(event) is WifiEvent:
            if  event.value == 0:
                self._wifi_level = 0
            elif event.value == 1:
                self._wifi_level = 5
            else:
                self._wifi_level = int(event.value * 5 + 1)
            self._display_wifi_level()
        elif type(event) is TextUpdateEvent and event.originator == TextFieldType.RANDOM_MSG:
            self._lcd.cursor_pos = (1, 0)
            self._lcd.write_string(event.value.ljust(20))
        elif type(event) is TextUpdateEvent and event.originator == TextFieldType.RADIO_NAME:
            self._lcd.cursor_pos = (2, 0)
            self._lcd.write_string(event.value.ljust(20))
        elif type(event) is TextUpdateEvent and event.originator == TextFieldType.TRACK_TITLE:
            self._lcd.cursor_pos = (3, 0)
            self._lcd.write_string(event.value.ljust(20))
        elif type(event) is StationButtonEvent:
            self.logger.debug("Event received : %s", event)
            if event.value == EncoderEvent.CW_ROTATION:
                self._owner.enter_choosing(True, self.track_nb + 1)
            elif event.value == EncoderEvent.CCW_ROTATION:
                self._owner.enter_choosing(True, self.track_nb - 1)
        return

    def cleanup(self):
        self.logger.debug("PlayingState cleaned up")
        self._random_msg_display.stop()
        self._name_display.stop()
        self._title_display.stop()


if __name__ == "__main__":
    # Resourcecs initialization
    rsc = Resources("/home/pi/python/webradio/conf.txt")
    # lcd initialization
    lcd = CharLCD(i2c_expander='PCF8574', address=0x3f, port=1,
              cols=20, rows=4, dotsize=8,
              charmap='A02',
              auto_linebreaks=True,
              backlight_enabled=True)
    lcd.backlight_enabled = True
    wifi = (
        0b00000,
        0b11111,
        0b00000,
        0b01110,
        0b00000,
        0b00100,
        0b00100,
        0b00000
        )
    lcd.create_char(0, wifi)

    state = PlayingState(lcd, rsc)
    state.enter_state()

    input("Entree pour quitter...")
    lcd.backlight_enabled = False


