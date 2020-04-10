#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 20:02:03 2018

@author: Sebastien Roy
"""

import random
import subprocess
import os.path
import os
import re
from shutil import copyfile
import logging

import RPi.GPIO as GPIO

from playingstate import PlayingState
from choosestationstate import ChooseStationState
from volumestate import VolumeState
from powerbutton import PowerEvent
from radiostate import RadioState
from radioevents import ChooseTimeoutEvent, PowerButtonEvent, VolumeButtonEvent, VolumeTimeoutEvent
from essidstate import EssidState, SleepState, PasswdState
from resources import Resources


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

class OffState(RadioState):
    """ This class defines the behaviour of the off state
    """
    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        self.logger = logging.getLogger(type(self).__name__)
        self._essid_state = EssidState(context, self)
        self._passwd_state = PasswdState(context, self)
        self._sleep_state = SleepState(context, self)
        self._sub_state = None

    def handle_event(self, event):
        self._sub_state.handle_event(event)

    def enter_state(self):
        self.logger.debug("Entering state")
        self._ctxt.power_button.led = False      
        proc = subprocess.Popen(["mpc", "stop"], stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        # switch off the soundcard
        mute_gpio = self._ctxt.rsc.mute_gpio
        if mute_gpio != 0:
            GPIO.output(mute_gpio, GPIO.LOW)

        self._sub_state = self._sleep_state
        self._sub_state.enter_state()

    def switch_radio(self, state):
        self._owner.switch_radio(state)

    def enter_choose_essid(self):
        self._sub_state.leave_state()
        self._sub_state = self._essid_state
        self._sub_state.enter_state()

    def enter_choose_pwd(self):
        self._sub_state.leave_state()
        self._sub_state = self._passwd_state
        self._sub_state.enter_state()

    def leave_state(self):
        self.logger.debug("Leaving state")
        self._sub_state.leave_state()

    def wifi_configured(self):
        essid = self._essid_state.essid
        password = self._passwd_state.password
        template = self._ctxt.rsc.wifi_template
        wpa_content = template.format(essid, password)
        wpa_filename = self._ctxt.rsc.wifi_filename
        try:
            backup_file(wpa_filename)
            f = open(wpa_filename, "w")
            f.write(wpa_content)
            f.close()
        except:
            print("Error while trying to save wpa file :", wpa_filename)
        lcd = self._ctxt.lcd
        lcd.clear()
        lcd.backlight_enabled = True
        lcd.cursor_pos = (0, 0)
        reboot = self._ctxt.rsc.get_i18n(Resources.REBOOT_ENTRY).ljust(20)
        lcd.write_string(reboot)
        # The reboot shall be written in the config file
        reboot_cmd = self._ctxt.rsc.wifi_post_validate
        subprocess.call(reboot_cmd.split(" "))

def backup_file(filename, last=99):
    logger = logging.getLogger(__name__)
    if not os.path.exists(filename):
        return
    logger.info("Backing up file : %s", filename)
    nb_size = len(str(last))
    # searching if already a backup file
    m = re.search("_back\d+$", filename)
    backup_filename = "" 
    nb = 0
    if m is None:
        backup_filename = filename + "_back" + str(1).zfill(nb_size)
    else:
        prefix = filename[:len(filename)-len(m.group(0))]
        nb_m = re.search("\d*$", m.group(0))
        nb = int(nb_m.group(0)) + 1
        backup_filename = prefix + "_back" + str(nb).zfill(nb_size)
        
    if nb < last:
        backup_file(backup_filename, last)

    copyfile(filename, backup_filename)
    logger.debug("End of backup of : %s", filename)
    return

if __name__ == "__main__":
    essid = "LesMetMs"
    password = "Tm1pC,mtvptf2l\'o"
    wpa_content = "network={{\n    ssid=\"{}\"\n    psk=\"{}\"\n}}".format(essid, password)
    print(wpa_content)

    filename = "/home/pi/python/tests/test.txt"
    if os.path.exists(filename):
        print("Creating a backup of file :", filename)
        basename = os.path.basename(filename)
        directory = os.path.dirname(filename)
        print("Basename :", basename)
        print("Dirname :", directory)
        print("Join :", os.path.join(directory, basename))
        backup_file(filename, 6)

    f = open(filename, "w")
    f.write(wpa_content)
    f.close()
        

        

        
    
    
    
