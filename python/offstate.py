#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 17:28:02 2020

@author: Sebastien Roy
"""
#import random
import subprocess
import os.path
import os
import re
from shutil import copyfile
import logging

import RPi.GPIO as GPIO

from radiostate import RadioState
from essidstate import EssidState, PasswdState
from sleepstate import SleepState
from resources import Resources

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

    def cleanup(self):
        self.logger.debug("deleting off state")
        self._essid_state.cleanup()
        self._passwd_state.cleanup()
        self._sleep_state.cleanup()

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
