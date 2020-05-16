#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 15:26:24 2020

@author: Sebastien ROY
"""

from radiostate import RadioState
from resources import Resources


class BtIdleState(RadioState):
    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        return

    def enter_state(self):
        # just display an idlle message
        bt_msg = self._ctxt.rsc.get_i18n(Resources.BT_PLAYBACK_ENTRY)
        self._ctxt.lcd.cursor_pos = (2, 0)
        self._ctxt.lcd.write_string(bt_msg)
        # last line is empty
        self._ctxt.lcd.cursor_pos = (3, 0)
        self._ctxt.lcd.write_string(" ".rjust(20))

        return

    def leave_state(self):
        return

    def handle_event(self, event):
        return

    def cleanup(self):
        return
