#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 18:32:07 2018

@author: Sebastien Roy
"""

from queue import Queue
from threading import Thread, Event
import time
import subprocess
import argparse
import traceback
import logging

import RPi.GPIO as GPIO
from RPLCD.i2c import CharLCD

from resources import Resources
from wifiscanner import WifiScanner
from radioevents import WifiEvent, StationButtonEvent, VolumeButtonEvent, PowerButtonEvent
from radiocontext import RadioContext
from onoffstate import OnState, OffState
from powerbutton import PowerButton
from encoder import RotaryEncoder

class WifiThread(Thread):
    """ A thread used to regulary check the wifi signal level
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
        """ Resules the thread
        """
        self._pause.set()

    def run(self):
        scanner = WifiScanner()
        while not self._stop:
            self._pause.wait()
            scanner.scan_wifi()

            quality = 0 if scanner.current_cell is None else scanner.current_cell.quality
            event = WifiEvent(quality)
            self._callback(event)
            time.sleep(5)


class MamemasRadio:
    """ Main class for the mamema's radio software.

        It initializes all the needed resources
        and then launches the radio state in sleeping mode.
    """

    def _power_callback(self, originator, event_type):
        event = PowerButtonEvent(event_type)
        self._event_queue.put(event)

    def _wifi_callback(self, event):
        self._event_queue.put(event)

    def _station_callback(self, originator, event_type):
        event = StationButtonEvent(event_type)
        self._event_queue.put(event)

    def _volume_callback(self, originator, event_type):
        event = VolumeButtonEvent(event_type)
        self._event_queue.put(event)

    def __init__(self, conf_path):
        self.logger = logging.getLogger(type(self).__name__)

        # Context initialisation

        self._rsc = Resources(conf_path)
        self._event_queue = Queue()
        self._init_playlist()
        lcd = self._init_lcd()
        power_button = PowerButton(self._rsc.power_switch, self._rsc.power_led, None)
        power_button.callback = self._power_callback
        station_gpios = self._rsc.station_button
        self._station_button = RotaryEncoder(station_gpios[0],
                                             station_gpios[1],
                                             station_gpios[2],
                                             callback=self._station_callback)
        volume_gpios = self._rsc.volume_button
        self._volume_button = RotaryEncoder(volume_gpios[0],
                                            volume_gpios[1],
                                            volume_gpios[2],
                                            callback=self._volume_callback)

        self._wifi_thread = WifiThread(self._wifi_callback)
        self._ctxt = RadioContext(self._rsc, lcd, power_button,
                                  self._station_button,
                                  self._volume_button,
                                  self._wifi_thread,
                                  self._event_queue)

        self._on_state = OnState(self._ctxt, self)
        self._off_state = OffState(self._ctxt, self)
        self._state = None
        # set callbacks

    def switch_radio(self, value):
        """ This method is called when the power button is pressed.
            The result is switching on or off the radio
        """
        if self._state is self._on_state and value:
            self.logger.error("Switch on when switched on should not happen")
        elif self._state is self._off_state and not value:
            self.logger.error("Switch off when switched off should not happen")
        else:
            self._state.leave_state()
            self._state = self._on_state if value else self._off_state
            self._state.enter_state()

    def _init_playlist(self):
        subprocess.call(["mpc", "clear"])
        playlist = self._rsc.playlist
        for entry, url in playlist:
            subprocess.call(["mpc", "add", url])

    def _init_lcd(self):
        lcd = CharLCD(i2c_expander='PCF8574', address=self._rsc.lcd_address,
                      port=1,
                      cols=20, rows=4, dotsize=8,
                      charmap='A00',
                      auto_linebreaks=True,
                      backlight_enabled=False)
        #self._lcd.backlight_enabled = False
        lcd.cursor_mode = "hide"
        wifi_char = (
            0b00000,
            0b11111,
            0b00000,
            0b01110,
            0b00000,
            0b00100,
            0b00100,
            0b00000
            )
        backspace_char = (
            0b00000,
            0b00000,
            0b00111,
            0b01001,
            0b10001,
            0b01001,
            0b00111,
            0b00000
                )
        enter_char = (
            0b00000,
            0b00001,
            0b00101,
            0b01001,
            0b11111,
            0b01000,
            0b00100,
            0b00000
            )

        lcd.create_char(0, wifi_char)
        lcd.create_char(1, backspace_char)
        lcd.create_char(2, enter_char)
        return lcd


    def start(self):
        """ This starts all the state model of the radio
        """
        self._state = self._off_state
        self._state.enter_state()
        self._wifi_thread.start()
        stopped = False
        while not stopped:
            try:
                event = self._event_queue.get()
                self.logger.info("Got event %s", event)
                self._state.handle_event(event)
                self._event_queue.task_done()
            except BaseException:
                self.logger.error("Stopped")
                self.logger.error(traceback.format_exc())
                self._wifi_thread.stop()
                self._ctxt.lcd.backlight_enabled = False
                self._ctxt.lcd.clear()
                self._ctxt.power_button.clear()
                self._ctxt.station_button.clear()
                self._ctxt.volume_button.clear()
                GPIO.cleanup()
                stopped = True


if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-c", "--config",
                            help="pathname of configuration file",
                            default="webradio.cfg")
    arg_parser.add_argument("-ll", "--log_level",
                            help="define logging level",
                            choices=["debug", "info", "warning", "error"],
                            default="info")
    arg_parser.add_argument("-lf", "--logfile",
                            help="define the logfile, console if none")
    args = arg_parser.parse_args()

    levels = {"debug": logging.DEBUG,
              "info": logging.INFO,
              "warning": logging.WARNING,
              "error": logging.ERROR}
    logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s',
                        level=logging.DEBUG
                        #filename=args.logfile
                        )
    logger = logging.getLogger(__name__)

    logging.info("Arguments : %s", args)
    logging.debug("This is debug information")

    radio = MamemasRadio(args.config)
    radio.start()
    