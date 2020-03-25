#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 20:52:52 2018

@author: Sebastien ROY
"""
from threading import Thread, RLock, Event
import time
import random
import logging


class ScrollingText:
        
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
                
                time.sleep(self._period)
                self._callback()
                
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
        self._update_thread = ScrollingText.TimerThread(refresh_rate, self.update_text)
        self._scroll_thread = ScrollingText.TimerThread(scroll_rate, self.scroll_text) 
        self.text = ""
        # The delay is currently computed as a number of refreshs
        self._scroll_begin_delay = scroll_begin_delay // scroll_rate if scroll_rate != 0 else scroll_begin_delay
        self._scroll_end_delay = scroll_end_delay // scroll_rate if scroll_rate != 0 else scroll_end_delay
        self._begin_counter = self._scroll_begin_delay
        self._end_counter = self._scroll_end_delay
        self._scroll_position = 0
        self._lock = RLock()
        self._paused = False
        
    def start(self):
        self.text = self._text_function()
        self.send_update(self.text)
        if self._refresh_rate > 0:
            self._update_thread.start()
        self._scroll_thread.start()
    
    def stop(self):
        self._paused = True
        self._scroll_thread.stop()
        if self._refresh_rate > 0:
            self._update_thread.stop()
           
        
    def pause(self):
        with self._lock:
            self._paused = True
            self._scroll_thread.pause()
            if self._refresh_rate > 0:
                self._update_thread.pause()
        
    def resume(self):
        self.text = self._text_function()
        self.logger.debug("Resuming {} with text={}".format(self, self.text))
        self.send_update(self.text)
        with self._lock:
            self._paused = False
            # when resuming, restart the scrolling
            self.scroll_position = 0
            self._begin_counter = self._scroll_begin_delay
            self._end_counter = self._scroll_end_delay
            self._scroll_thread.resume()
            if self._refresh_rate > 0:
                self._update_thread.resume()

    def send_update(self, value):
        if len(value) <= self._display_size:
            self._update_callback(self, value)
        else:
            self._update_callback(self, value[:self._display_size])
       
    
    def update_text(self):
        with self._lock:
            if self._paused:
                return
            new_text = self._text_function()
            if new_text != self.text:       # text changed !
                self.text = new_text
                self.scroll_position = 0
                self._begin_counter = self._scroll_begin_delay
                self._end_counter = self._scroll_end_delay
                self.send_update(new_text)
    
    def scroll_text(self):
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
            elif (self.scroll_position + self._display_size) < len(self.text):
                self.scroll_position += 1
                displayed_text = self.text[self.scroll_position : self.scroll_position + self._display_size]
                self._update_callback(self, displayed_text)
            # check if it the pause at the end of the scrolling
            elif self._end_counter > 0:
                self._end_counter -= 1
            # restart at the beginning
            else:
                self.scroll_position = 0
                self._begin_counter = self._scroll_begin_delay
                self._end_counter = self._scroll_end_delay
                self._update_callback(self, self.text[0:self._display_size])
                
    
    def _get_text(self):
        with self._lock:
            return self.text
    
def _test_callback(originator, text):
    print("Update from {} with text : {}".format(originator, text))
    
def _test_text_function():
    values = ["titi", "tata", "tutu", "toto"]
    value = random.choice(values);
    print("text = ", value)
    return value

def _test_text_function2():
    return "voila"

def _test_long_text():
    return "C'est l'histoire d'un monsieur"
    
    
if __name__ == "__main__":
    scroll = ScrollingText(_test_long_text, _test_callback, 10, 1)
    print("Strarting scrolling text...")
    try:
        scroll.start()
        while True:
            input("Press enter to pause")
            scroll.pause()
            input("Press enter to resume")
            scroll.resume()
    finally:
        scroll.stop()
    
    
        