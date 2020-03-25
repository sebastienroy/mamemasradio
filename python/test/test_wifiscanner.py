import unittest


#import WifiCell
from wifiscanner import WifiCell, WifiProbe , WifiScanner

class ProbeMockup():
    """ ProbeMockup replaces WifiProbe for testing purpose
    """
    def get_iwgetid(self):
        return "wlan0     ESSID:\"My Wifi Network\""
    def get_iwlist(self, interface = "wlan0"):
        return "wlan0     Scan completed :\n\
          Cell 01 - Address: B0:B2:8F:A3:56:E4\n\
                    Channel:44\n\
                    Frequency:5.22 GHz (Channel 44)\n\
                    Quality=51/70  Signal level=-59 dBm  \n\
                    Encryption key:on\n\
                    ESSID:\"My Wifi Network\"\n\
                    Bit Rates:6 Mb/s; 9 Mb/s; 12 Mb/s; 18 Mb/s; 24 Mb/s\n\
                              36 Mb/s; 48 Mb/s; 54 Mb/s\n\
                    Mode:Master\n\
                    Extra:tsf=0000000000000000\n\
                    Extra: Last beacon: 26470ms ago\n\
                    IE: Unknown: 000D42626F782D3246314342313445\n\
                    IE: Unknown: 01088C1218243048606C\n\
                    IE: Unknown: 03012C\n\
                    IE: Unknown: 050400010000\n\
                    IE: Unknown: 07104652202401172801172C011730011700\n\
                    IE: Unknown: 0B05010001FFFF\n\
                    IE: Unknown: 46050000000000\n\
                    IE: Unknown: 200100\n\
                    IE: Unknown: C3050217171700\n\
                    IE: Unknown: 2A0100\n\
                    IE: Unknown: 2D1AEF0117FFFFFFFFFEFFFFFFFF1F000001000000000018E6E71900\n\
                    IE: Unknown: 3D162C050400000000000000000000000000000000000000\n\
                    IE: Unknown: DD180050F2020101830003A4000027A4000042435E0062322F00\n\
                    IE: IEEE 802.11i/WPA2 Version 1\n\
                        Group Cipher : CCMP\n\
                        Pairwise Ciphers (1) : CCMP\n\
                        Authentication Suites (1) : PSK\n\
                    IE: WPA Version 1\n\
                        Group Cipher : CCMP\n\
                        Pairwise Ciphers (1) : CCMP\n\
                        Authentication Suites (1) : PSK\n\
                    IE: Unknown: BF0CB279CB3FAAFF0000AAFF0000\n\
                    IE: Unknown: C005012A00FCFF\n\
                    IE: Unknown: DD1E002686010300DD00000025040892000601B05BEB98730000000000000000\n\
                    IE: Unknown: DD06002686170000\n\
                    IE: Unknown: 7F080100080200000040\n\
                    IE: Unknown: DD390050F204104A000110104400010210570001011049000600372A000120105800188387EDA7C059EA71CAC362685DF5C3550001010103007FC5\n\
          Cell 02 - Address: E2:D0:83:52:F0:A7\n\
                    Channel:1\n\
                    Frequency:2.412 GHz (Channel 1)\n\
                    Quality=70/70  Signal level=-27 dBm  \n\
                    Encryption key:on\n\
                    ESSID:\"Ouaisouais\"\n\
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 6 Mb/s; 9 Mb/s\n\
                              11 Mb/s; 12 Mb/s; 18 Mb/s\n\
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s\n\
                    Mode:Master\n\
                    Extra:tsf=0000000000000000\n\
                    Extra: Last beacon: 26470ms ago\n\
                    IE: Unknown: 000A4F756169736F75616973\n\
                    IE: Unknown: 010882848B0C12961824\n\
                    IE: Unknown: 32043048606C\n\
                    IE: Unknown: 030101\n\
                    IE: Unknown: 2A0104\n\
                    IE: IEEE 802.11i/WPA2 Version 1\n\
                        Group Cipher : CCMP\n\
                        Pairwise Ciphers (1) : CCMP\n\
                        Authentication Suites (1) : PSK\n\
                    IE: Unknown: 2D1A2D0117FF00000000000000000000000000000000000000000000\n\
                    IE: Unknown: 3D1601000000000000000000000000000000000000000000\n\
                    IE: Unknown: DD180050F2020101000003A4000027A4000042435E0062322F00\n\
                    IE: Unknown: DD050016328000\n\
                    IE: Unknown: DD080050F21102000000\n"
    

class test_WifiScanner(unittest.TestCase):
    
    
    
    def setUp(self):
        self.cell_output = "          Cell 05 - Address: CA:FB:1E:B1:CA:2F\n\
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

    def test_WifiProbe(self):
        probe = WifiProbe()
        self.assertIsNotNone(probe.get_iwgetid())
        self.assertIsNotNone(probe.get_iwlist())
 
        
    def test_WifiCell(self):
        
        lines = self.cell_output.split("\n")
        cell = WifiCell(lines[0])
        for line in lines[1:]:
            cell.append_line(line)
                
        self.assertEqual(cell.cell_number, 5)
        self.assertEqual(cell.address, "CA:FB:1E:B1:CA:2F")
        self.assertEqual(cell.channel, 12)
        self.assertEqual(cell.frequency, 2.467)
        self.assertAlmostEqual(cell.quality, 32./70.)
        self.assertEqual(cell.signal_level, -78)
        self.assertEqual(cell.essid, "FreeWifi_secure")
        
    def test_WifiScanner(self):
        #scanner = WifiScanner(ProbeMockup())
        #scanner.scan_wifi()
        scanner = WifiScanner()
        probe = ProbeMockup()
        scanner = WifiScanner(probe)
        
        scanner.scan_wifi()
        self.assertEqual(scanner.essid, "My Wifi Network")
        self.assertEqual(len(scanner.cells),2)
        self.assertEqual(scanner.current_cell.essid, "My Wifi Network")
        self.assertAlmostEqual(scanner.current_cell.quality, 51./70.)
        
        self.assertTrue(True)


        