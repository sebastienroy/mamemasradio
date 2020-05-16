#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 10 19:38:01 2020

@author: Sébastien ROY
"""
import logging
import subprocess
import random
import datetime
import time
from threading import Thread, Event

import RPi.GPIO as GPIO

from radiostate import RadioState
from volumestate import VolumeState
from btidlestate import BtIdleState
from resources import Resources
from scrollingtext import ScrollingText
from radioevents import TextUpdateEvent, TextFieldType, PowerButtonEvent, StationButtonEvent, VolumeButtonEvent, VolumeTimeoutEvent
from powerbutton import PowerEvent
from encoder import EncoderEvent

class BlinkingThread(Thread):
    """ A thread used to blink the display background when bluetooth is discoverable
    """
    def __init__(self, callback):
        Thread.__init__(self)
        self._callback = callback
        self._stop = False
        self._pause = Event()

    def stop(self):
        """ Stops the thread
        """
        self._stop = True

    def pause(self):
        """ Pauses the thread
        """
        self._pause.clear()

    def resume(self):
        """ Resumes the thread
        """
        self._pause.set()

    def run(self):
        while not self._stop:
            self._pause.wait()
            time.sleep(0.5)
            self._callback()


class BluetoothState(RadioState):
    """ Bluetooth state is entered when the radio is off and the user press the
    station button. The bluetooth state allows to play from a phone (for instance)
    to the radio through bluetooth.
    There is two substates :
        - BtPlayback, that is the entry substate of the bluetooth state. The is
        Nothing more
        - BtDiscoverable, that allows bt client devices to discover the radio.
    """

    def __init__(self, context, owner):
        RadioState.__init__(self, context, owner)
        self.logger = logging.getLogger(type(self).__name__)

        # Random msg inittialisation
        self.random_msg = ""
        self._random_msg_display = ScrollingText(self._random_msg, self._random_msg_callback,
                                           display_size=20, refresh_rate=0,
                                           scroll_begin_delay=self._ctxt.rsc.scroll_begin,
                                           scroll_end_delay=self._ctxt.rsc.scroll_end,
                                           scroll_rate=self._ctxt.rsc.scroll_rate)
        self._random_msg_display.start()
        self._random_msg_display.pause()

        # clock initialisation
        self._clock_rolling_text = ScrollingText(self._get_time_text,
                                                 self._time_callback,
                                                 display_size=5,
                                                 refresh_rate=1)
        self._clock_rolling_text.start()
        self._clock_rolling_text.pause()

        self._blink_thread = None
        self._blinking = False
        # substates
        self._volume_state = VolumeState(self._ctxt, self)
        self._idle_state = BtIdleState(self._ctxt, self)
        self._sub_state = None
        
        # ensure the bluetooth device is pairable
        subprocess.call(["bluetoothctl", "pairable", "on"])

        return

    def enter_state(self):
        """ Assumption : the Audio Profile Sink Role has been enabled
            switch on soundcard
            echo "power on" | bluetoothctl
            echo "pairable on" | bluetoothctl
            bluealsa-aplay 00:00:00:00:00:00
        """
        self.logger.debug("Entering BluetoothState ")

        self.random_msg = self._ctxt.rsc.today_msg
        if not self.random_msg:
            self.random_msg = random.choice(self._ctxt.rsc.random_msgs)

         # switch on the soundcard
        mute_gpio = self._ctxt.rsc.mute_gpio
        if mute_gpio != 0:
            GPIO.output(mute_gpio, GPIO.HIGH)
        # power on the bluetooth stuff
        subprocess.call(["bluetoothctl", "power", "on"])
        # play what users want to
        self._aplay_proc = subprocess.Popen(["bluealsa-aplay","00:00:00:00:00:00"])

        self._ctxt.lcd.clear()
        self._ctxt.lcd.backlight_enabled = True
        self._ctxt.power_button.led = True

        self._display_welcome()

        self._sub_state = self._idle_state
        self._sub_state.enter_state()

        self._clock_rolling_text.resume()
        self._random_msg_display.resume()
        return

    def leave_state(self):
        #close all the bluetooth stuff
        self._aplay_proc.kill()
        #subprocess.call(["bluetoothctl" ,"pairable", "off"])
        subprocess.call(["bluetoothctl", "power", "off"])

        self._stop_blinking()
        self._clock_rolling_text.pause()
        self._random_msg_display.pause()
        return

    def handle_event(self, event):
        if type(event) is PowerButtonEvent and event.value == PowerEvent.SWITCH_PRESSED:
            self._owner.switch_radio(True)
        elif type(event) is StationButtonEvent and event.value == EncoderEvent.SWITCH_PRESSED:
            # TODO : switch to discoverabe during a few seconds
            if self._blinking :
                self._stop_blinking()
            else:
                self._start_blinking()
        elif type(event) is VolumeTimeoutEvent:
            self._leave_volume()
        elif type(event) is VolumeButtonEvent:
            self._change_volume(event)
        elif type(event) is TextUpdateEvent and event.originator == TextFieldType.RANDOM_MSG:
            self._ctxt.lcd.cursor_pos = (1, 0)
            self._ctxt.lcd.write_string(event.value.ljust(20))
        elif type(event) is TextUpdateEvent and event.originator == TextFieldType.BT_CLOCK:
            self.logger.debug("writing clock string : %s", event.value)
            self._ctxt.lcd.cursor_pos = (0, 15)
            self._ctxt.lcd.write_string(event.value.rjust(5))
        return

    def cleanup(self):
        return

    def _leave_volume(self):
        if self._sub_state == self._volume_state:
            self._sub_state.leave_state()
            self._sub_state = self._idle_state
            self._sub_state.enter_state()

    def _change_volume(self, event):
        if self._sub_state == self._volume_state:
            self._sub_state.handle_event(event)
        else:
            self._volume_state.increment(event.value)
            self._sub_state.leave_state()
            self._sub_state = self._volume_state
            self._sub_state.enter_state()

    def _display_welcome(self):
         msg = self._ctxt.rsc.welcome_msg.ljust(Resources.WELCOME_MSG_MAX_SIZE)
         self._ctxt.lcd.cursor_pos = (0, 0)
         self._ctxt.lcd.write_string(msg)
         return

    def _get_time_text(self):
        dtg = datetime.datetime.today()
        return dtg.strftime(self._ctxt.rsc.clock_format)

    def _time_callback(self, originator, value):
        self.logger.debug("_time_callback called")
        self._ctxt.event_queue.put(TextUpdateEvent(value, TextFieldType.BT_CLOCK))

    def _random_msg_callback(self, originator, value):
        self._ctxt.event_queue.put(TextUpdateEvent(value, TextFieldType.RANDOM_MSG))

    def _random_msg(self):
        return self.random_msg

    def _start_blinking(self):
        self.logger.debug("switch to discoverable")
        self._blinking_starttime = time.time()
        self._blink_thread = BlinkingThread(self.blink)
        self._blink_thread.start()
        self._blink_thread.resume()
        subprocess.call(["bluetoothctl", "discoverable", "on"])

    def _stop_blinking(self):
        if self._blink_thread is not None:
            self._blink_thread.stop()
            self._blink_thread = None
        self._ctxt.lcd.backlight_enabled = True
        subprocess.call(["bluetoothctl", "discoverable", "off"])

    def blink(self):
        self.logger.debug("Blink!")
        self._ctxt.lcd.backlight_enabled = not(self._ctxt.lcd.backlight_enabled)
        if self._ctxt.lcd.backlight_enabled \
                and (time.time() - self._blinking_starttime) > self._ctxt.rsc.bt_discoverable_timeout:
            self._stop_blinking()
