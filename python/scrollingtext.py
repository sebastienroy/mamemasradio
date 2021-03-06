#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 20:52:52 2018

@author: Sebastien ROY
"""
from threading import Thread, RLock, Event
import time
import logging

class ScrollingText:
    """ Tool class that manages a string that scrolls into a given frame.
        The Scrolling text is initialized using a text function, a text callback,
        a refresh rate, a scoll rate. In order to make easier the reading at
        the begin and at the end of ths scrolling, there is also a begin and
        and end scrolling delay.
        The refresh rate is used to refresh the content of the text, using
        the text function
        The scrolling text may be used for instance to manage the text displayed
        on a 4x20 LCD screen.
        stop() function should be used in order to free resources
    """

    class TimerThread(Thread):
        def __init__(self, period, callback):
            Thread.__init__(self)
            self._period = period
            self._callback = callback
            self._stop = False
            self._pause = Event()
            self._pause.set()

        def stop(self):
            self._stop = True

        def run(self):
            while not self._stop:
                self._pause.wait()
                self._callback()

                time.sleep(self._period)

        def pause(self):
            self._pause.clear()

        #should just resume the thread
        def resume(self):
            self._pause.set()


    def __init__(self, text_function, update_callback, display_size, refresh_rate=0,
                 scroll_begin_delay=3, scroll_end_delay=3, scroll_rate=0.5):
        self.logger = logging.getLogger(type(self).__name__)
        self._text_function = text_function
        self._update_callback = update_callback
        self._display_size = display_size
        self._refresh_rate = refresh_rate
        self._scroll_rate = scroll_rate
        self._update_thread = ScrollingText.TimerThread(refresh_rate, self._update_text)
        self._scroll_thread = ScrollingText.TimerThread(scroll_rate, self._scroll_text)
        self.text = ""
        # The delay is currently computed as a number of refreshs
        self._scroll_begin_delay = scroll_begin_delay // scroll_rate \
            if scroll_rate != 0 \
            else scroll_begin_delay
        self._scroll_end_delay = scroll_end_delay // scroll_rate \
            if scroll_rate != 0 \
            else scroll_end_delay
        self._begin_counter = self._scroll_begin_delay
        self._end_counter = self._scroll_end_delay
        self._scroll_position = 0
        self._lock = RLock()
        self._paused = False
        self.logger.debug("Scrolling text %s initialized", self)

    def start(self):
        """ Can only be called once
        """
        self.text = self._text_function()
        self._send_update(self.text)
        if self._refresh_rate > 0:
            self._update_thread.start()
        self._scroll_thread.start()
        self.logger.debug("Scrolling text %s started with text \"%s\"", self, self.text)

    def stop(self):
        """ Be carefull, one stopped, the scrolling text cannot be restarted
            Use pause() and resume() instead.
        """
        self._paused = True
        self._scroll_thread.stop()
        if self._refresh_rate > 0:
            self._update_thread.stop()
        self.logger.debug("Scrolling text %s stopped", self)


    def pause(self):
        """ Pauses the scrolling text. No scroll is paused, the text is
            not updated
        """
        with self._lock:
            self._paused = True
            self._scroll_thread.pause()
            if self._refresh_rate > 0:
                self._update_thread.pause()
            self.logger.debug("Scrolling text %s paused with current position = %d",
                              self, self._scroll_position)

    def resume(self):
        """ Resumes the scrolling text. The text restarts from the beginning
        """
        self.text = self._text_function()
        self._send_update(self.text)
        with self._lock:
            self._paused = False
            # when resuming, restart the scrolling
            self._scroll_position = 0
            self._begin_counter = self._scroll_begin_delay
            self._end_counter = self._scroll_end_delay
            self._scroll_thread.resume()
            if self._refresh_rate > 0:
                self._update_thread.resume()
            self.logger.debug("Scrolling text %s resumed with text \"%s\"",
                              self, self.text)

    def _send_update(self, value):
        if len(value) <= self._display_size:
            self._update_callback(self, value)
        else:
            self._update_callback(self, value[:self._display_size])


    def _update_text(self):
        with self._lock:
            if self._paused:
                return
            new_text = self._text_function()
            if new_text != self.text:       # text changed !
                self.text = new_text
                self._scroll_position = 0
                self._begin_counter = self._scroll_begin_delay
                self._end_counter = self._scroll_end_delay
                self._send_update(new_text)

    def _scroll_text(self):
        with self._lock:
            # check if a scrolling is necessary
            if self._paused:
                return
            elif len(self.text) <= self._display_size:
                return
            # check if the scrolling shall be started
            elif self._begin_counter > 0:
                self._begin_counter -= 1
            # check if not at the end of the scroll
            elif (self._scroll_position + self._display_size) < len(self.text):
                self._scroll_position += 1
                displayed_text = self.text[self._scroll_position : self._scroll_position + self._display_size]
                self._update_callback(self, displayed_text)
            # check if it the pause at the end of the scrolling
            elif self._end_counter > 0:
                self._end_counter -= 1
            # restart at the beginning
            else:
                self._scroll_position = 0
                self._begin_counter = self._scroll_begin_delay
                self._end_counter = self._scroll_end_delay
                self._update_callback(self, self.text[0:self._display_size])


    def _get_text(self):
        with self._lock:
            return self.text
