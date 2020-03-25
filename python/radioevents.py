#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 19:16:11 2018

@author: Sebastien ROY
"""

from enum import Enum

class RadioEvent:
    def __init__(self, value = None, originator = None):
        self.value = value
        self.originator = originator
        
    def __repr__(self):
        return "RadioEvent: Value={} Originator={}".format(self.value, self.originator)
        
    

class WifiEvent(RadioEvent):
    def __init__(self, value):
        RadioEvent.__init__(self, value=value)
        
    def __repr__(self):
        return "WifiEvent: Value={}".format(self.value)
        
class TextFieldType(Enum):
    RANDOM_MSG = 1
    RADIO_NAME = 2
    TRACK_TITLE = 3
    
class TextUpdateEvent(RadioEvent):
    def __init__(self, value, text_field):
        RadioEvent.__init__(self, value=value, originator=text_field)
        
    def __repr__(self):
        return "TextUpdateEvent: Value={} Originator={}".format(self.value, self.originator)

class StationButtonEvent(RadioEvent):
    # In StationButtonEvent, no need of the originator. 
    #   because there is only one Station button
    def __init__(self, value):
        RadioEvent.__init__(self, value=value)
        
    def __repr__(self):
        return "StationButtonEvent: value = {}".format(self.value)

class VolumeButtonEvent(RadioEvent):
    # In StationButtonEvent, no need of the originator. 
    #   because there is only one Station button
    def __init__(self, value):
        RadioEvent.__init__(self, value=value)
        
    def __repr__(self):
        return "VolumeButtonEvent: value = {}".format(self.value)
    
class PowerButtonEvent(RadioEvent):
    # In StationButtonEvent, no need of the originator. 
    #   because there is only one Station button
    def __init__(self, value):
        RadioEvent.__init__(self, value=value)
        
    def __repr__(self):
        return "PowerButtonEvent: value = {}".format(self.value)

  
class ChooseTimeoutEvent(RadioEvent):
    def __init__(self):
        RadioEvent.__init__(self)
        
class VolumeTimeoutEvent(RadioEvent):
    def __init__(self):
        RadioEvent.__init__(self)
    
if __name__ == "__main__":
    event = TextUpdateEvent("Hello", TextFieldType.RADIO_NAME)
    
    print(event.originator)
    