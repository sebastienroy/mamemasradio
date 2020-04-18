#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 12:34:19 2018

@author: Sebastien Roy
"""

import configparser
import datetime
import logging


class Resources:
    """ This class is used to get all the values from configuration files
    """
    GENERAL_SECTION = "general"
    WELCOME_ENTRY = "welcome_msg"
    DEFAULT_WELCOME_MSG = "Bonjour Maman!"
    SCROLL_RATE_ENTRY = "scroll_rate"
    SCROLL_BEGIN_ENTRY = "scroll_begin_delay"
    SCROLL_END_ENTRY = "scroll_end_delay"
    CHOOSE_TIMEOUT_ENTRY = "choose_timout"
    VOLUME_TIMEOUT_ENTRY = "volume_timout"
    VOLUME_INCREMENT_ENTRY = "volume_increment"

    WIFI_SECTION = "wifi"
    WIFI_FILENAME_ENTRY = "filename"
    WIFI_TEMPLATE_ENTRY = "template"
    POST_VALIDATE_ENTRY = "post_validate"

    I18N_SECTION = "i18n"
    NO_TITLE_ENTRY = "no_title_msg"
    CHANGE_STATION_ENTRY = "change_station"
    CONFIRM_CHANGE_ENTRY = "confirm_change"
    NETWORK_CHOICE_ENTRY = "network_choice"
    PLEASE_TURN_ENTRY = "please_turn"
    PLEASE_PRESS_ENTRY = "please_press"
    ENTER_PWD_ENTRY = "enter_pwd"
    PRESS_ENTER_ENTRY = "press_enter"
    REBOOT_ENTRY = "reboot"
    VOLUME_MSG_ENTRY = "volume"

    RANDOM_MSG_SECTION = "random_messages"
    DATED_MSG_SECTION = "dated_messages"
    PLAYLIST_SECTION = "playlist"

    WELCOME_MSG_MAX_SIZE = 16
    MSG_MAX_SIZE = 20

    HARDWARE_SECTION = "hardware"
    LCD_ADDRESS_ENTRY = "lcd_address"
    POWER_SWITCH_ENTRY = "power_switch"
    POWER_LED_ENTRY = "power_led"
    STATION_BUTTON_ENTRY = "station_button"
    VOLUME_BUTTON_ENTRY = "volume_button"
    MUTE_ENTRY = "mute"

    SLEEP_SECTION = "sleep"
    
    CLOCK_SECTION = "clock"
    CLOCK_FORMAT_ENTRY = "format"

    def __init__(self, config_file_path):
        self.logger = logging.getLogger(type(self).__name__)
        self._configParser = configparser.RawConfigParser()
        self._config_file_path = config_file_path
        self._welcome_msg = ""
        try:
            self._configParser.read(config_file_path, encoding='utf-8')
            self._welcome_msg = self._configParser.get(Resources.GENERAL_SECTION,
                                                       Resources.WELCOME_ENTRY)

            entries = self._configParser.items(Resources.RANDOM_MSG_SECTION)
            self._msgs = [y for x, y in entries]
            sleep_entries = self._configParser.items(Resources.SLEEP_SECTION)
            self._sleep_lines = [y.strip("\"") for x, y in sleep_entries]
            if len(self._sleep_lines) > 4:
                self._sleep_lines = self._sleep_lines[:4]

        except configparser.NoSectionError as nosection:
            self.logger.error("Error: %s in configuration file: %s",
                              nosection,
                              self._config_file_path)
        except configparser.NoOptionError as nosection:
            self.logger.error("Error: %s in configuration file: %s",
                              nosection,
                              self._config_file_path)
        return

    def get_i18n(self, entry):
        return self._configParser.get(Resources.I18N_SECTION, entry)

    def _get_lcd_address(self):
        address = ""
        try:
            address = self._configParser.get(Resources.HARDWARE_SECTION,
                                             Resources.LCD_ADDRESS_ENTRY)
        except:
            address = "0x27"
        return int(address, 0)  # let it guess the base from the format

    def _get_welcome_msg(self):
        msg = self._welcome_msg if self._welcome_msg \
                        else Resources.DEFAULT_WELCOME_MSG
        return msg if len(msg) <= Resources.WELCOME_MSG_MAX_SIZE \
                        else msg[0: Resources.WELCOME_MSG_MAX_SIZE]

    def _get_today_msg(self):
        today_msg = ""
        today = datetime.date.today()
        dated_msgs = self._configParser.items(Resources.DATED_MSG_SECTION)
        for key, msg in dated_msgs:
            day_month = key.split("/")
            day = int(day_month[0])
            month = int(day_month[1])
            if day == today.day and month == today.month:
                today_msg = msg
                break
        return today_msg;

    def _get_msgs(self):
        return self._msgs

    def _get_power_switch(self):
        str = self._configParser.get(Resources.HARDWARE_SECTION, Resources.POWER_SWITCH_ENTRY)
        return int(str, 0)

    def _get_power_led(self):
        str = self._configParser.get(Resources.HARDWARE_SECTION, Resources.POWER_LED_ENTRY)
        return int(str, 0)

    def _get_sleep_lines(self):
        return self._sleep_lines

    def _get_clock_format(self):
        return self._configParser.get(Resources.CLOCK_SECTION,
                                      Resources.CLOCK_FORMAT_ENTRY)

    def _get_wifi_filename(self):
        return self._configParser.get(Resources.WIFI_SECTION,
                                      Resources.WIFI_FILENAME_ENTRY)

    def _get_wifi_template(self):
        return self._configParser.get(Resources.WIFI_SECTION,
                                      Resources.WIFI_TEMPLATE_ENTRY)

    def _get_wifi_post_validate(self):
        return self._configParser.get(Resources.WIFI_SECTION,
                                      Resources.POST_VALIDATE_ENTRY)

    def _get_scroll_rate(self):
        return float(self._configParser.get(Resources.GENERAL_SECTION,
                                            Resources.SCROLL_RATE_ENTRY))

    def _get_scroll_begin(self):
        return float(self._configParser.get(Resources.GENERAL_SECTION,
                                            Resources.SCROLL_BEGIN_ENTRY))

    def _get_scroll_end(self):
        return float(self._configParser.get(Resources.GENERAL_SECTION,
                                            Resources.SCROLL_END_ENTRY))

    def _get_choose_timeout(self):
        return float(self._configParser.get(Resources.GENERAL_SECTION,
                                            Resources.CHOOSE_TIMEOUT_ENTRY))

    def _get_volume_timeout(self):
        return float(self._configParser.get(Resources.GENERAL_SECTION,
                                            Resources.VOLUME_TIMEOUT_ENTRY))

    def _get_volume_increment(self):
        return float(self._configParser.get(Resources.GENERAL_SECTION,
                                            Resources.VOLUME_INCREMENT_ENTRY))

    def _get_playlist(self):
        return self._configParser.items(Resources.PLAYLIST_SECTION)

    def _get_station_button(self):
        str = self._configParser.get(Resources.HARDWARE_SECTION, Resources.STATION_BUTTON_ENTRY)
        return [int(val.strip()) for val in str.split(",")]

    def _get_volume_button(self):
        str = self._configParser.get(Resources.HARDWARE_SECTION, Resources.VOLUME_BUTTON_ENTRY)
        return [int(val.strip()) for val in str.split(",")]

    def _get_mute_gpio(self):
        return int(self._configParser.get(Resources.HARDWARE_SECTION,
                                      Resources.MUTE_ENTRY))

    welcome_msg = property(fget=_get_welcome_msg)
    lcd_address = property(fget=_get_lcd_address)
    random_msgs = property(fget=_get_msgs)
    today_msg = property(fget=_get_today_msg)
    power_switch = property(fget=_get_power_switch)
    power_led = property(fget=_get_power_led)
    sleep_lines = property(fget=_get_sleep_lines)
    clock_format = property(fget=_get_clock_format)
    wifi_filename = property(fget=_get_wifi_filename)
    wifi_template = property(fget=_get_wifi_template)
    wifi_post_validate = property(fget=_get_wifi_post_validate)
    scroll_rate = property(fget=_get_scroll_rate)
    scroll_begin = property(fget=_get_scroll_begin)
    scroll_end = property(fget=_get_scroll_end)
    choose_timeout = property(fget=_get_choose_timeout)
    volume_timeout = property(fget=_get_volume_timeout)
    volume_increment = property(fget=_get_volume_increment)
    playlist = property(fget=_get_playlist)
    station_button = property(fget=_get_station_button)
    volume_button = property(fget=_get_volume_button)
    mute_gpio = property(fget=_get_mute_gpio)


if __name__ == "__main__":
    print("Test 1")
    rsc = Resources("/home/pi/python/webradio/conf.txt")
    print(rsc.welcome_msg)

    print("Test 2")
    rsc = Resources("unknown.txt")
    print(rsc.welcome_msg)

    print("Test 3")
    rsc = Resources("/home/pi/python/webradio/conf_test3.txt")
    print(rsc.welcome_msg)

    print("Test 4")
    rsc = Resources("/home/pi/python/webradio/conf_test4.txt")
    print(rsc.welcome_msg)

    print("Test 5")
    rsc = Resources("/home/pi/python/webradio/conf.txt")
    print("Lcd address found in file = {}".format(rsc.lcd_address))

    print("Test 6")
    rsc = Resources("unknown.txt")
    print("Lcd address NOT found in file = {}".format(rsc.lcd_address))

    print("Test 7")
    rsc = Resources("/home/pi/python/webradio/conf.txt")
    print("Random messages :", rsc.random_msgs)

    print("Test 8")
    print(rsc._configParser["playlist"])
    for key, value in enumerate(rsc._configParser["playlist"]):
        print("key={} ; value={} ; value2={}".format(key, value,
                                                     rsc._configParser["playlist"][value]))

    print("Test 9")
    print("Playlist", rsc._configParser.items("playlist"))
    x, y = rsc._configParser.items("playlist")[5]
    print(x)
    print("Station buttons :", rsc.station_button)
    print("Sleep lines :", rsc.sleep_lines)
    print("Today msg :", rsc.today_msg)

    template = rsc.wifi_template
    print("Formated wpa_supplicant file :")
    print(template.format("MyESSID", "MyPassword"))
