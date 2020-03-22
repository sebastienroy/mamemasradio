#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 19:29:51 2018

@author: pi
"""

import subprocess
import logging

from radiostate import RadioState
from wifiscanner import WifiScanner
from radioevents import StationButtonEvent, PowerButtonEvent
from encoder import EncoderEvent
from powerbutton import PowerEvent
from resources import Resources

class EssidState(RadioState):
    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        self.logger = logging.getLogger(type(self).__name__)
        self._essid_nb = 0
        self._ids = []
        self.essid=""
        
    def enter_state(self):
        self.logger.debug("Entering state")
        rsc = self._ctxt.rsc
        net_choice = rsc.get_i18n(Resources.NETWORK_CHOICE_ENTRY).ljust(20)
        please_turn = rsc.get_i18n(Resources.PLEASE_TURN_ENTRY).ljust(20)
        please_press = rsc.get_i18n(Resources.PLEASE_PRESS_ENTRY).ljust(20)
        
        lcd = self._ctxt.lcd
#        rsc = self._ctxt.rsc
        lcd.clear()
        lcd.backlight_enabled = True
        lcd.cursor_pos = (0, 0)
        lcd.write_string(net_choice)
        lcd.cursor_pos = (1, 0)
        lcd.write_string(please_turn)
        lcd.cursor_pos = (2, 0)
        lcd.write_string(please_press)
        scanner = WifiScanner()
        scanner.scan_wifi()
        self._ids = [cell.essid for cell in scanner.cells]
        self.logger.info("Available ESSIDs : %s", self._ids)
        self._essid_nb = 0
        self.essid=""
        if len(self._ids) > 0:
            self.display_essid()
        
    def handle_event(self, event):
        if type(event) is PowerButtonEvent and event.value == PowerEvent.SWITCH_PRESSED:
            self._owner.switch_radio(True)
        elif type(event) is StationButtonEvent:
            if event.value == EncoderEvent.CW_ROTATION:
                if self._essid_nb >= len(self._ids) - 1:
                    self._essid_nb = 0
                else:
                    self._essid_nb += 1
                self.display_essid()
            elif event.value == EncoderEvent.CCW_ROTATION:
                if self._essid_nb == 0:
                    self._essid_nb = len(self._ids) - 1
                else:
                    self._essid_nb -= 1
                self.display_essid()
            elif event.value == EncoderEvent.SWITCH_PRESSED:
                self.essid = self._ids[self._essid_nb]
                self._owner.enter_choose_pwd()
            
    def display_essid(self):
        lcd = self._ctxt.lcd
        lcd.cursor_pos = (3, 0)
        lcd.write_string(self._ids[self._essid_nb].ljust(20))
        
        
class SleepState(RadioState):
    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        self.logger = logging.getLogger(type(self).__name__)
        self.encoder_pressed = False
        
    def enter_state(self):
        self.logger.debug("Entering state")
        self._ctxt.lcd.clear()
        self._ctxt.lcd.backlight_enabled = False
        self._ip_displayed = False
        self.encoder_pressed = False
        lines = []
        lines = self._ctxt.rsc.sleep_lines
        for i, line in enumerate(lines):
            self._ctxt.lcd.cursor_pos=(i, 0)
            self._ctxt.lcd.write_string(line.ljust(20))

    def handle_event(self, event):
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

class PasswdState(RadioState):
    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        self.logger = logging.getLogger(type(self).__name__)
        self.password = ""
        self._allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!\"#$%&'()*+,-./:;<=>?@[]^_`{|}\x01\x02"
        self._chars_pos = 0
        self._cursor_pos = 0
        
    def enter_state(self):
        self.logger.debug("Entering state")
        rsc = self._ctxt.rsc
        enter_pwd = rsc.get_i18n(Resources.ENTER_PWD_ENTRY).ljust(20)
        press_enter = "\x02 pour valider".ljust(20)
        
        lcd = self._ctxt.lcd
        lcd.clear()
        lcd.backlight_enabled = True
        lcd.cursor_pos = (0, 0)
        lcd.write_string(enter_pwd)
        lcd.cursor_pos = (1, 0)
        lcd.write_string(press_enter)
        self.display_passwd()
        self.display_chars()
        
    def leave_state(self):
        self.logger.debug("Leaving state")
        self._ctxt.lcd.cursor_mode = "hide"

    def handle_event(self, event):
        if type(event) is PowerButtonEvent and event.value == PowerEvent.SWITCH_PRESSED:
            self._owner.switch_radio(True)
        elif type(event) is StationButtonEvent:
            length = len(self._allowed_chars)
            if event.value == EncoderEvent.CW_ROTATION:
                if self._cursor_pos < 19:   # size of text is greater than 20, no test to do
                    self._cursor_pos += 1
                    self._update_cursor()
                elif length - self._chars_pos > 20:
                    self._chars_pos +=1
                    self.display_chars()
            elif event.value == EncoderEvent.CCW_ROTATION:
                if self._cursor_pos > 0:
                    self._cursor_pos -= 1
                    self._update_cursor()
                elif self._chars_pos > 0:
                    self._chars_pos -= 1
                    self.display_chars()
            elif event.value == EncoderEvent.SWITCH_PRESSED:
                pos = self._chars_pos + self._cursor_pos
                if pos < length - 2:
                    self.password = self.password + self._allowed_chars[pos]
                    self.display_passwd()
                    self.display_chars()
                elif pos == length - 2 and self.password:   # Backspace char
                    self.password = self.password[0 : len(self.password) - 1]
                    self.display_passwd()
                    self.display_chars()
                elif pos == length - 1:     # The last char is the "Enter" char
                    self._owner.wifi_configured()
                return
    
    def _update_cursor(self):
        self._ctxt.lcd.cursor_pos = (2, self._cursor_pos)

                         
    def display_chars(self):
        lcd = self._ctxt.lcd
        lcd.cursor_mode = "hide"
        lcd.cursor_pos = (2, 0)
        lcd.write_string(self._allowed_chars[self._chars_pos : self._chars_pos + 20])
        lcd.cursor_pos = (2, self._cursor_pos)
        lcd.cursor_mode = "blink"

    def display_passwd(self):
        lcd = self._ctxt.lcd
        lcd.cursor_mode = "hide"
        lcd.cursor_pos = (3, 0)
        length = len(self.password)
        if length < 20:
            lcd.write_string(self.password.ljust(20))
        else:
            lcd.write_string(self.password[length - 20 : length])
        
