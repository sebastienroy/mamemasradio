#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 20:07:30 2018

@author: Sebastien ROY
"""


class RadioContext:
    """ This class holds all the context elements needed by the radio soft :
        lcd, resources, etc
        """
    def __init__(self, rsc, lcd, power_button, station_button, volume_button, wifi_thread,
                 event_queue):
        self.rsc = rsc
        self.lcd = lcd
        self.power_button = power_button
        self.volume_button = volume_button
        self.station_button =station_button
        self.wifi_thread = wifi_thread
        self.event_queue = event_queue
        return


