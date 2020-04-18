#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 11:29:31 2018

@author: Sebastien ROY
"""

from threading import Thread, Event
import time

from wifiscanner import WifiScanner
from radioevents import WifiEvent

class WifiThread(Thread):
    def __init__(self, callback):
        Thread.__init__(self)
        self._callback = callback
        self._stop = False
        self._event = Event()
        self._event.set()

    def stop(self):
        self._stop = True
        return

    def pause(self):
        self._event.clear()
        return

    def resume(self):
        self._event.set()
        return


    def run(self):
        scanner = WifiScanner()
        while not self._stop:
            self._event.wait()
            scanner.scan_wifi()
            quality = scanner.current_cell.quality
            event = WifiEvent(quality)
            self._callback(self, event)
            time.sleep(1)

def _test_callback(originator, event):
    print(event)

if __name__ == "__main__":
    thread = WifiThread(_test_callback)
    thread.start()
    input("Enter to pause the tread")
    thread.pause()
    input("Enter to resume the thread")
    thread.resume()
    input("Enter to finish")
    thread.stop()