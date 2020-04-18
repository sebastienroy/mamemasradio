#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 16:36:16 2018

@author: Sebastien Roy
"""

import subprocess
import re

import time

interface = "wlan0"


class WifiCell:
    """ WifiCell is a tool class used by WifiScanner to parse Wifi network

    Once parsed by WifiScanner, the cells can be requested for their properties

        Properties:
            essid
            quality
            signal_level
            cell_number
            channel
            frequency
    """

    _cell_pattern = re.compile("(?<=Cell).*")
    _address_pattern = re.compile("(?<=Address:).*")
    _channel_pattern = re.compile("(?<=Channel:).*")
    _frequency_pattern = re.compile("(?<=Frequency:).*")
    _quality_pattern = re.compile("(?<=Quality=).*")
    _signal_pattern = re.compile("(?<=Signal level=).*")
    _essid_pattern = re.compile("(?<=ESSID:).*")

    def __init__(self,line):
        self._cell_number = 0
        self._address = ""
        self._essid = ""
        self._quality = 0.0
        self._channel = 0
        self._signal_level = 0
        self._frequency = 0.0
        self._parse_cell(line)
        return

    def _parse_cell(self, line):
        m = WifiCell._cell_pattern.search(line)
        if m is not None:
            content = m.group(0).split("-")
            try:
                self._cell_number = int(content[0])
                address = content[1].strip();
                m2 = WifiCell._address_pattern.search(address)
                if m2 is not None:
                    self._address = m2.group(0).strip()

            except :
                #TODO : handle that
                print("Exception in parsing")
        return

    def append_line(self, line):
        """This methods try to find the following properties in the line :
            Channel
            Frequency
            Quality
            Signal level
            ESSID
        """
        if self._channel == 0 :     # Do not check it twice
            match = WifiCell._channel_pattern.search(line)
            if(match is not None):
                self._channel = int(match.group(0))
                return
        if self._frequency == 0.0 :
            match = WifiCell._frequency_pattern.search(line)
            if(match is not None):
                self._frequency = float(match.group(0).split(" ")[0])
                return
        if self._quality == 0.0 :
            match = WifiCell._quality_pattern.search(line)
            if(match is not None):
                fraction = match.group(0).split(" ")[0].split("/")
                self._quality = float(fraction[0])/float(fraction[1])
            # Signal level is on the same line than Quality
            match = WifiCell._signal_pattern.search(line)
            if(match is not None):
                self._signal_level = int(match.group(0).split(" ")[0])
            return
        if not self._essid :
            match = WifiCell._essid_pattern.search(line)
            if(match is not None):
                self._essid = match.group(0).strip().strip("\"")
                return
        return


    def _get_cell_number(self):
        return self._cell_number
    cell_number = property(_get_cell_number)

    def _get_address(self):
        return self._address
    address = property(_get_address)

    def _get_channel(self):
        return self._channel
    channel = property(_get_channel)

    def _get_frequency(self):
        return self._frequency
    frequency = property(_get_frequency)

    def _get_quality(self):
        return self._quality
    quality = property(_get_quality)

    def _get_signal_level(self):
        return self._signal_level
    signal_level = property(_get_signal_level)

    def _get_essid(self):
        return self._essid
    essid = property(_get_essid)


class WifiProbe:
    """ This is is a tool class intended to get output strings from the system.
        It is used by WifiScanner
        For testing it may be replaced with test classes
    """

    def get_iwgetid(self):
        """
            Returns the output of 'iwgetid' command,
            wich contains the interface information and the ESSID information
            from the wifi interface
        """
        proc = subprocess.Popen(["iwgetid"],stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        return out

    def get_iwlist(self, interface = "wlan0"):
        """
            Returns the result of the system command 'iwlist wlan0 scan'
            Wich contains the description of all accessible wifi cells
        """
        proc = subprocess.Popen(["iwlist", interface, "scan"],stdout=subprocess.PIPE, universal_newlines=True)
        out, err = proc.communicate()
        return out



class WifiScanner:
    """ WifiScanner is a tool used to extract wifi network information

        Once the wifi network is scanned, the WifiScanner can return a list
        of reachable cells and also the current wifi cell.
        A cell is a WifiCell object.
        See WifiCell description for its properties
        The essid can also be requested directly from WifiScanner object.

        Usage :
            # scan wifi network
            scanner = WifiScanner()
            scanner.scan_wifi()
            # display result
            print("The wifi connected ESSID is : {}".format(scanner.essid))
            print("There are currently {} reachable wifi cells".format(len(scanner.cells)))
            print("The connected wifi quality is {} (1 is maximum)".format(scanner.current_cell.quality))

    """

    def __init__(self, probe = WifiProbe()):
        self._cells = []
        self._essid = ""
        self._probe = probe
        # self._interface = interface
        self._current_cell = None
        return

    def scan_wifi(self):
        """ scans the wifi
        """
        self._current_cell = None
        self._cells = []

        iwid = self._probe.get_iwgetid()
        m = re.search("(?<=ESSID:).*", iwid)
        if m is not None:
            self._essid = m.group(0).strip("\"")
        else:
            self._essid = ""

        wlan = iwid.split()[0]
        iwlist = self._probe.get_iwlist(wlan)

        cell = None
        for line in iwlist.split("\n"):
            cell_match = re.match("^[ ]*Cell ",line)
            if cell_match is not None:
                # then create a new cell
                cell = WifiCell(line)
                self._cells.append(cell)
            elif cell is not None:
                cell.append_line(line)
            # check if the previous parsed cell is the used one

        for cell in self._cells:
            if self._essid and cell.essid == self._essid:
                self._current_cell = cell
                break

    def _get_essid(self):
        return self._essid

    def _get_interface(self):
        return self._interface

    def _get_cells(self):
        return self._cells

    def _get_current_cell(self):
        return self._current_cell

    essid = property(_get_essid)
    interface = property(_get_interface)
    cells = property(_get_cells)
    current_cell = property(_get_current_cell)


if __name__ == "__main__":

    output = "          Cell 05 - Address: CA:FB:1E:B1:CA:2F\n\
                    Channel:12\n\
                    Frequency:2.467 GHz (Channel 12)\n\
                    Quality=32/70  Signal level=-78 dBm  \n\
                    Encryption key:on\n\
                    ESSID:\"FreeWifi_secure\"\n\
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 9 Mb/s\n\
                              18 Mb/s; 36 Mb/s; 54 Mb/s\n\
                    Bit Rates:6 Mb/s; 12 Mb/s; 24 Mb/s; 48 Mb/s\n\
                    Mode:Master\n\
                    Extra:tsf=0000000000000000\n\
                    Extra: Last beacon: 10ms ago\n\
                    IE: Unknown: 000F46726565576966695F736563757265\n\
                    IE: Unknown: 010882848B961224486C\n\
                    IE: Unknown: 03010C\n\
                    IE: Unknown: 2A0104\n\
                    IE: Unknown: 32040C183060\n\
                    IE: Unknown: 2D1A6E1017FFFF000001000000000000000000000000000000000000\n\
                    IE: Unknown: 3D160C000600000000000000000000000000000000000000\n\
                    IE: Unknown: 3E0100\n\
                    IE: WPA Version 1\n\
                        Group Cipher : CCMP\n\
                        Pairwise Ciphers (1) : CCMP\n\
                        Authentication Suites (1) : 802.1x\n\
                    IE: Unknown: DD180050F2020101000003A4000027A4000042435E0062322F00\n\
                    IE: Unknown: 7F0101\n\
                    IE: Unknown: DD07000C4300000000\n\
                    IE: Unknown: DD1E00904C336E1017FFFF000001000000000000000000000000000000000000\n\
                    IE: Unknown: DD1A00904C340C000600000000000000000000000000000000000000"
    lines = output.split("\n")
    t0 = time.clock()
    cell = WifiCell(lines[0])
    for line in lines[1:]:
        cell.append_line(line)
    t1 = time.clock()

    print("Cell = %{}%".format(cell.cell_number))
    print("Address = %{}%".format(cell.address))
    print("Channel = %{}%".format(cell.channel))
    print("Frequency = %{}%".format(cell.frequency))
    print("Quality = %{}%".format(cell.quality))
    print("Signal level = %{}%".format(cell.signal_level))
    print("ESSID = %{}%".format(cell.essid))
    print("Process time :", t1-t0)

    print("---------------------------")
    scanner = WifiScanner()
    scanner.scan_wifi()
    print("")
    for cell in scanner.cells:
        print("Cell = %{}%".format(cell.cell_number))
        print("Address = %{}%".format(cell.address))
        print("Channel = %{}%".format(cell.channel))
        print("Frequency = %{}%".format(cell.frequency))
        print("Quality = %{}%".format(cell.quality))
        print("Signal level = %{}%".format(cell.signal_level))
        print("ESSID = %{}%".format(cell.essid))
        print()

    for i in range (0,10):
        scanner.scan_wifi()
        quality = 0 if scanner.current_cell is None else scanner.current_cell.quality
        print("CurrentCell quality :", quality)
        if not scanner.current_cell is None:
            print("Essid :", scanner.current_cell.essid)
        time.sleep(5)

