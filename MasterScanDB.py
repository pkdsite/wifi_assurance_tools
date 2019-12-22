'''
File:
    MasterScanDB.py
Description:
    The aim of this script is to generate Wi-Fi scan information from any
    platform OS and structured it into a Json format and it also stored in the
    Sqlite3 database. While executing this script make sure Sqlite3 database
    must be installed in your system.
Author:
    Milap J. Bhuva
    SOPHOS-ML-NSG
'''

import sys
import re
import platform
import subprocess
import json
import sqlite3
from datetime import datetime, date


def ensure_str(output):
    '''
    Takecare about different platform outputs
    '''
    try:
        output = output.decode("utf8")
    except UnicodeDecodeError:
        output = output.decode("utf16")
    except AttributeError:
        pass
    return output


def quality_to_rssi(quality):
    '''
    Converts Signal_Quality to dbm
    '''
    return int((quality / 2) - 100)


def bytes_to_MB(B):
    '''
    Converts the given bytes to KB, MB, GB, or TB string
    '''
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2)  # 1,048,576
    GB = float(KB ** 3)  # 1,073,741,824
    TB = float(KB ** 4)  # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return '{0:.2f} KB'.format(B/KB)
    elif MB <= B < GB:
        return '{0:.2f} MB'.format(B/MB)
    elif GB <= B < TB:
        return '{0:.2f} GB'.format(B/GB)
    elif TB <= B:
        return '{0:.2f} TB'.format(B/TB)


def channel_to_channelwidth(Channel):
    '''
    Identify Cahnnel Width
    '''
    list_20MHz = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
                  '12', '13', '14', '15', '16', '36', '40', '44', '48', '52',
                  '56', '60', '64', '100', '104', '108', '112', '116', '120',
                  '124', '128', '132', '136', '140', '144', '149', '153',
                  '157', '161', '165', '169', '173']
    list_40MHz = ['34', '38', '46', '54', '62', '102', '110', '118', '126',
                  '134', '142', '151', '159',
                  '1,+1', '2,-1', '2,+1', '3,-1', '3,+1', '4,-1', '4,+1',
                  '5,-1', '5,+1', '6,-1', '6,+1', '7,-1', '7,+1',
                  '8,-1', '8,+1', '9,-1', '9,+1', '10,-1', '10,+1',
                  '11,-1', '11,+1', '12,-1', '12,+1', '13,-1', '13,+1',
                  '14,-1',
                  '36,+1', '40,-1', '44,+1', '48,-1', '52,+1', '56,-1',
                  '60,+1', '64,-1', '100,+1', '104,-1', '108,+1', '112,-1',
                  '116,+1', '120,-1', '124,+1', '128,-1', '132,+1', '136,+1',
                  '149,+1', '153,-1', '157,+1', '161,-1', '165,+1', '169,-1',
                  '1+2', '2-1', '3+4', '4-3', '5+6', '6-5', '7+8', '8-7',
                  '9+10', '10-9', '11+12', '12-11', '13+14', '14-13', '36+40',
                  '40-36', '44+48', '48-44', '52+56', '56-52', '60+64',
                  '64-60', '100+104', '104-100', '108+112', '112-108',
                  '116+120', '120-116', '124+128', '128-124', '132+136',
                  '136+140', '149+153', '153-149', '157+161', '161-157',
                  '165+169', '169-165', '2+3']
    list_80MHz = ['42', '58', '106', '122', '138', '155']
    list_160MHz = ['50', '114']

    channelStr = str(Channel)
    if channelStr in list_20MHz:
        return('20 MHz')
    elif channelStr in list_40MHz:
        return('40 MHz')
    elif channelStr in list_80MHz:
        return('80 MHz')
    elif channelStr in list_160MHz:
        return('160 MHz')


def channel_to_frequency(Channel):
    '''
    Identify Frequency for corresponding Channel
    '''
    freq_dict = {
        "1": "2.412 GHz", "2": "2.417 GHz", "3": "2.422 GHz", "4": "2.427 GHz",
        "5": "2.432 GHz", "6": "2.437 GHz", "7": "2.442 GHz", "8": "2.447 GHz",
        "9": "2.452 GHz", "10": "2.457 GHz", "11": "2.462 GHz",
        "12": "2.467 GHz", "13": "2.472 GHz", "14": "2.484 GHz",
        "34": "5.170 GHz", "36": "5.180 GHz", "40": "5.200 GHz",
        "44": "5.220 GHz", "48": "5.240 GHz", "50": "5.250 GHz",
        "52": "5.260 GHz", "54": "5.270 GHz", "56": "5.280 GHz",
        "58": "5.290 GHz", "60": "5.300 GHz", "62": "5.310 GHz",
        "64": "5.320 GHz", "100": "5.500 GHz", "104": "5.520 GHz",
        "108": "5.540 GHz", "112": "5.560 GHz", "116": "5.580 GHz",
        "120": "5.600 GHz", "124": "5.620 GHz", "128": "5.640 GHz",
        "132": "5.660 GHz", "136": "5.680 GHz", "140": "5.700 GHz",
        "144": "5.720 GHz", "149": "5.745 GHz", "151": "5.755 GHz",
        "153": "5.765 GHz", "155": "5.775 GHz", "157": "5.785 GHz",
        "159": "5.795 GHz", "161": "5.805 GHz", "165": "5.825 GHz",
        "169": "5.845 GHz", "173": "5.865 GHz",
        "1,+1": "2.417 GHz", "2,-1": "2.412 GHz", "2,+1": "2.422 GHz",
        "3,+1": "2.427 GHz", "3,-1": "2.417 GHz",
        "4,-1": "2.422 GHz", "4,+1": "2.432 GHz",
        "5,-1": "2.427 GHz", "5,+1": "2.437 GHz",
        "6,-1": "2.432 GHz", "6,+1": "2.442 GHz",
        "7,-1": "2.437 GHz", "7,+1": "2.447 GHz",
        "8,-1": "2.442 GHz", "8,+1": "2.452 GHz",
        "9,-1": "2.447 GHz", "9,+1": "2.457 GHz",
        "10,-1": "2.452 GHz", "10,+1": "2.462 GHz",
        "11,-1": "2.457 GHz", "11,+1": "2.467 GHz",
        "12,-1": "2.462 GHz", "12,+1": "2.472 GHz",
        "13,-1": "2.467 GHz", "13,+1": "2.484 GHz",
        "14,-1": "2.472 GHz",
        "36,+1": "5.200 GHz", "40,-1": "5.180 GHz",
        "44,+1": "5.240 GHz", "48,-1": "5.220 GHz", "52,+1": "5.280 GHz",
        "56,-1": "5.260 GHz", "60,+1": "5.320 GHz", "64,-1": "5.300 GHz",
        "100,+1": "5.520 GHz", "104,-1": "5.500 GHz", "108,+1": "5.560 GHz",
        "112,-1": "5.540 GHz", "116,+1": "5.600 GHz", "120,-1": "5.580 GHz",
        "124,+1": "5.640 GHz", "128,-1": "5.620 GHz", "132,+1": "5.680 GHz",
        "136,+1": "5.700 GHz", "149,+1": "5.765 GHz", "153,-1": "5.745 GHz",
        "157,+1": "5.805 GHz", "161,-1": "5.785 GHz", "165,+1": "5.845 GHz",
        "169,-1": "5.825 GHz",
        "1+2": "2.417 GHz", "2-1": "2.412 GHz", "3+4": "2.427 GHz",
        "4-3": "2.422 GHz", "5+6": "2.437 GHz", "6-5": "2.432 GHz",
        "7+8": "2.447 GHz", "8-7": "2.442 GHz", "9+10": "2.457 GHz",
        "10-9": "2.452 GHz", "11+12": "2.467 GHz", "12-11": "2.462 GHz",
        "13+14": "2.484 GHz", "14-13": "2.472 GHz", "2+3": "2.422 GHz",
        "36+40": "5.200 GHz", "40-36": "5.180 GHz",
        "44+48": "5.240 GHz", "48-44": "5.220 GHz", "52+56": "5.280 GHz",
        "56-52": "5.260 GHz", "60+64": "5.320 GHz", "64-60": "5.300 GHz",
        "100+104": "5.520 GHz", "104-100": "5.500 GHz",
        "108+112": "5.560 GHz", "112-108": "5.540 GHz",
        "116+120": "5.600 GHz", "120-116": "5.580 GHz",
        "124+128": "5.640 GHz", "128-124": "5.620 GHz",
        "132+136": "5.680 GHz", "136+140": "5.700 GHz",
        "149+153": "5.765 GHz", "153-149": "5.745 GHz",
        "157+161": "5.805 GHz", "161-157": "5.785 GHz",
        "165+169": "5.845 GHz", "169-165": "5.825 GHz"
    }

    '''
    display list of keys
    '''
    # key = list(freq_dict.keys())
    # print(key)

    '''
    display list of values
    '''
    # value = list(freq_dict.values())
    # print(value)

    '''
    display list of items (k -> v)
    '''
    # item = list(freq_dict.items())
    # print(item)

    try:
        channelStr = str(Channel)
        Frequency = freq_dict[channelStr]
        # print(Channel, Frequency)
        return Frequency
    except KeyError:
        pass


def check_and_validate_bssid(array):
    modifiedBssid = []

    for bssid in array:
        splitedBssid = bssid.split(":")
        tempArray = []

        for byte in splitedBssid:
            if len(byte) < 2:
                byte = "0" + byte
            tempArray.append(byte)

        modifiedBssid.append(":".join(tempArray))
    return modifiedBssid


class AccessPoint(dict):

    def __init__(self, mode, SSID, BSSID, Signal, Channel, ChannelWidth,
                 Frequency, Authentication, PCipher, GCipher, NetworkType,
                 HT="null", CC="null",
                 State="null", Rx="null", Tx="null", MAC="null"):
        if mode == "interface":
            dict.__init__(self, SSID=SSID, BSSID=BSSID,
                          State=State, Rx=Rx, Tx=Tx, MAC=MAC)
        elif mode == "network":
            dict.__init__(self, SSID=SSID, BSSID=BSSID, Signal=Signal,
                          Channel=Channel, ChannelWidth=ChannelWidth,
                          Frequency=Frequency, Authentication=Authentication,
                          PCipher=PCipher, GCipher=GCipher,
                          NetworkType=NetworkType, HT=HT, CC=CC,
                          State=State, Rx=Rx, Tx=Tx, MAC=MAC)


class WifiScanner(object):
    '''
    General methods declaration
    '''

    def __init__(self, device):
        self.device = device
        self.cmd = self.get_cmd()

    def get_access_points(self):
        interface, network = self.call_subprocess(self.cmd)
        results_interface = self.parse_output_interface(ensure_str(interface))
        results_network = self.parse_output_network(ensure_str(network))
        return (results_interface, results_network)

    @staticmethod
    def call_subprocess(cmd):
        proc1 = subprocess.Popen(cmd[0], stdout=subprocess.PIPE, shell=True)
        proc2 = subprocess.Popen(cmd[1], stdout=subprocess.PIPE, shell=True)
        (interface, _) = proc1.communicate()
        (network, _) = proc2.communicate()
        return (interface, network)


class WINRadioScanner(WifiScanner):
    '''
    Generate Wi-Fi information for Windows system
    '''
    def get_cmd(self):
        return ("netsh wlan show interface",
                "netsh wlan show networks mode=bssid")

    def parse_output_interface(self, output):
        State = None
        State_line = -100
        HT = "null"
        CC = "null"
        results = []
        for num, line in enumerate(output.split("\n")):
            line = line.strip()
            if line.startswith("Physical address"):
                MAC = ":".join(line.split(":")[1:]).strip()
            elif line.startswith("State"):
                State = " ".join(line.split()[2:]).strip().replace("connected",
                                                                   "Connected")
                State_line = num
            elif num == State_line + 1:
                SSID = ":".join(line.split(":")[1:]).strip()
            elif num == State_line + 2:
                BSSID = ":".join(line.split(":")[1:]).strip()
            elif num == State_line + 3:
                NetworkType = ":".join(line.split(":")[1:]).strip()
            # elif num == State_line + 4:
            #     RadTyp = ":".join(line.split(":")[1:]).strip()
            elif num == State_line + 5:
                Authentication = ":".join(line.split(":")[1:]).strip()
            elif num == State_line + 6:
                PCipher = ":".join(line.split(":")[1:]).strip()
                GCipher = ":".join(line.split(":")[1:]).strip()
            elif num == State_line + 8:
                Channel = int(":".join(line.split(":")[1:]).strip())
            elif num == State_line + 9:
                Rx = float(":".join(line.split(":")[1:]).strip())
            elif num == State_line + 10:
                Tx = float(":".join(line.split(":")[1:]).strip())
            elif num == State_line + 11:
                quality = int(":".join(line.split(":")[1:]).strip()
                              .replace("%", ""))
                if State is not None:
                    ap = AccessPoint("interface", SSID, BSSID,
                                     quality_to_rssi(int(quality)), Channel,
                                     channel_to_channelwidth(Channel),
                                     channel_to_frequency(Channel),
                                     Authentication, PCipher,
                                     GCipher, NetworkType,
                                     HT, CC, State, Rx, Tx, MAC)
                    results.append(ap)
        return results

    def parse_output_network(self, output):
        SSID = None
        SSID_line = -100
        BSSID = None
        BSSID_line = -100
        results = []
        for num, line in enumerate(output.split("\n")):
            line = line.strip()
            if line.startswith("SSID"):
                SSID = " ".join(line.split()[3:]).strip()
                if SSID == '':
                    # truely empty SSID
                    SSID = ' '
                if SSID == '!@#$%^&*()_+=-][|\';?/,.+_)(*&^':
                    SSID = 'SQL INJECTION ALERT DONT CONNECT WITH THIS'
                SSID_line = num
            elif num == SSID_line + 1:
                NetworkType = ":".join(line.split(":")[1:]).strip()
            elif num == SSID_line + 2:
                Authentication = ":".join(line.split(":")[1:]).strip()
            elif num == SSID_line + 3:
                PCipher = ":".join(line.split(":")[1:]).strip()
                GCipher = ":".join(line.split(":")[1:]).strip()
            elif line.startswith("BSSID"):
                BSSID = ":".join(line.split(":")[1:]).strip()
                BSSID_line = num
            elif num == BSSID_line + 1:
                quality = int(":".join(line.split(":")[1:]).strip()
                              .replace("%", ""))
            # elif num == BSSID_line + 2:
            #     RadTyp = ":".join(line.split(":")[1:]).strip()
            elif num == BSSID_line + 3:
                Channel = int(":".join(line.split(":")[1:]).strip())
                if BSSID is not None:
                    ap = AccessPoint("network", SSID, BSSID,
                                     quality_to_rssi(int(quality)), Channel,
                                     channel_to_channelwidth(Channel),
                                     channel_to_frequency(Channel),
                                     Authentication, PCipher,
                                     GCipher, NetworkType)
                    results.append(ap)
        return results


class LINRadioScanner(WifiScanner):
    '''
    Generate Wi-Fi information for Linux system
    '''
    def get_cmd(self):
        # return "iwconfig {} 2>/dev/null".format(self.device)
        return ("interface=`ifconfig | awk '/wlp/{print$1}'`; \
                 iw $interface link",
                "sudo iwlist {} scanning 2>/dev/null".format(self.device))

    def parse_output_interface(self, output):
        SSID = None
        BSSID = None
        Channel = "null"
        Authentication = "null"
        PCipher = "null"
        GCipher = "null"
        NetworkType = "null"
        HT = "null"
        CC = "null"
        MAC = "null"
        results = []
        for _, line in enumerate(output.split("\n")):
            line = line.strip()
            if line.startswith("SSID"):
                SSID = ":".join(line.split(":")[1]).strip()
            elif line.startswith("freq"):
                Frequency = ":".join(line.split(":")[1]).strip()
                Frequency = float(Frequency[:1] + "." + Frequency[1:])
            elif line.startswith("Connected"):
                BSSID = ":".join(line.split("to")[1]).strip()
                BSSID = re.findall(r"(?:[0-9a-fA-F]:?){12}", BSSID)[0]
                State = re.findall(r"Connected", line)[0]
            elif line.startswith("RX"):
                Rx = ":".join(line.split(":")[1]).strip()
                Rx = float(re.findall(r"\d+", Rx)[0])
            elif line.startswith("TX"):
                Tx = ":".join(line.split(":")[1]).strip()
                Tx = float(re.findall(r"\d+", Tx)[0])
            elif line.startswith("signal"):
                Signal = ":".join(line.split(":")[1]).strip()
                Signal = int(re.findall(r"-\d+", Signal)[0])
                if BSSID is not None:
                    ap = AccessPoint("interface", SSID, BSSID, Signal,
                                     Channel, channel_to_channelwidth(Channel),
                                     Frequency, Authentication, PCipher,
                                     GCipher, NetworkType, HT, CC, State,
                                     bytes_to_MB(Rx), bytes_to_MB(Tx), MAC)
                    results.append(ap)
        return results

    def parse_output_network(self, output):
        SSID = None
        BSSID = None
        BSSID_line = -1000000
        Signal = "null"
        Channel = "null"
        Frequency = "null"
        Authentication = "null"
        PCipher = "null"
        GCipher = "null"
        NetworkType = "null"
        State = "null"
        Rx = "null"
        Tx = "null"
        MAC = "null"
        results = []
        for num, line in enumerate(output.split("\n")):
            line = line.strip()
            if line.startswith("Cell"):
                if BSSID is not None:
                    ap = AccessPoint("network", SSID, BSSID, Signal, Channel,
                                     channel_to_channelwidth(Channel),
                                     Frequency, Authentication,
                                     PCipher, GCipher, NetworkType, State,
                                     Rx, Tx, MAC)
                    results.append(ap)
                BSSID = ":".join(line.split(":")[1:]).strip().lower()
                BSSID_line = num
            elif line.startswith("Channel"):
                Channel = int(":".join(line.split(":")[1:]).strip())
            elif line.startswith("Frequency"):
                Frequency = ":".join(line.split(":")[1:]).strip()[:9]
            elif line.startswith("ESSID"):
                SSID = ":".join(line.split(":")[1:]).strip().strip('"')
            elif num > BSSID_line + 2 and re.search(r"\d/\d", line):
                Signal = int(line.split("=")[2].split(" ")[0])
                BSSID_line = -1000000000
            elif line.startswith("Authentication"):
                Authentication = str(
                               ":".join(line.split(":")[1:])
                               .strip().split(" ")[0])
            elif line.startswith("Pairwise Cipher"):
                PCipher = ":".join(line.split(":")[1:]).strip()
            elif line.startswith("Group Cipher"):
                GCipher = ":".join(line.split(":")[1:]).strip()
                # if BSSID is not None:
                #     ap = AccessPoint("network", SSID, BSSID, Signal,
                #                    Channel, channel_to_channelwidth(Channel),
                #                    Frequency, Authentication, PCipher,
                #                    GCipher,NetworkType, State, Rx, Tx, MAC)
                #     results.append(ap)
        return results


class OSXRadioScanner(WifiScanner):
    '''
    Generate Wi-Fi information for MACOS system
    '''
    def get_cmd(self):
        return ("/System/Library/PrivateFrameworks/Apple80211.framework/" +
                "Versions/Current/Resources/airport /usr/sbin/airport -I",
                "/System/Library/PrivateFrameworks/Apple80211.framework/" +
                "Versions/Current/Resources/airport /usr/sbin/airport -s")

    def parse_output_interface(self, output):
        results = []
        bssidTemp = []
        State = None
        Authentication = "null"
        PCipher = "null"
        GCipher = "null"
        HT = "null"
        CC = "null"
        MAC = "null"
        for _, line in enumerate(output.split("\n")):
            line = line.strip()
            if line.startswith("SSID"):
                SSID = ":".join(line.split(":")[1]).strip()
            elif line.startswith("BSSID"):
                BSSID = bssidTemp.append(":".join(line.split(":")[1:]).strip())
                BSSID = check_and_validate_bssid(bssidTemp)[0]
            elif line.startswith("state"):
                State = str(
                      ":".join(line.split(":")[1]).strip().replace(
                        "running", "Connected"))
            elif line.startswith("channel"):
                Channel = ":".join(line.split(":")[1]).strip()
            elif line.startswith("agrCtlRSSI"):
                Signal = ":".join(line.split(":")[1]).strip()
            elif line.startswith("lastTxRate"):
                Tx = float(":".join(line.split(":")[1]).strip())
            elif line.startswith("maxRate"):
                Rx = float(":".join(line.split(":")[1]).strip())
                # print("RXs:", bytes_to_MB(250790436864))
            elif line.startswith("op mode"):
                NetworkType = ":".join(line.split(":")[1]).strip()
        if State is not None:
            ap = AccessPoint("interface", SSID, BSSID, Signal, Channel,
                             channel_to_channelwidth(Channel),
                             channel_to_frequency(Channel),
                             Authentication, PCipher, GCipher, NetworkType,
                             HT, CC, State, Rx, Tx, MAC)
            results.append(ap)
        return results

    def parse_output_network(self, string):
        NetworkType = "null"
        State = "null"
        Rx = "null"
        Tx = "null"
        MAC = "null"
        results = []
        for line in string.split('\n'):
            p = re.compile(r'(?:[0-9a-fA-F]:?){12}')
            # Find BSSID:
            BSSID = re.findall(p, line)

            found_BSSID = False
            # Split string to get SSID
            for match in re.finditer(p, line):  # There will be just one
                BSSID_start_idx = match.start()
                BSSID_end_idx = match.end()
                found_BSSID = True
            if found_BSSID is False:
                continue  # It's the first line, with the name of each column.

            BSSID = BSSID[0]

            # Left side of BSSID
            SSID = line[:BSSID_start_idx].lstrip().rstrip()

            # Right side of BSSID. Chop the string to the 1st char after BSSID
            line = line[BSSID_end_idx:].lstrip()   # Chop line until on RSSI
            Signal = int(line[:line.find(' ')])    # RSSI is between and ' '

            line = line[line.find(' '):].lstrip()  # Chop line until on Channel
            Channel_str = line[:line.find(' ')]    # Channel is between and ' '
            Channel = Channel_str.split(' ')[0]
            channel = int(Channel_str.split(',')[0])

            # if re.match(r'^[0-9]+[,][-+]?[0-9]*', Channel_sec):
            #     print(Channel)
            #     ChannelWidth = '40 MHz'
            # else:
            #     ChannelWidth = '20 MHz'

            line = line[line.find(' '):].lstrip()  # Chop line until on HT
            HT = line[0]                           # HT is 1 Character

            line = line[line.find(' '):].lstrip()  # Chop line until on CC
            CC = line[:2]                          # CC is the 2 first chars

            line = line[line.find(' '):].lstrip()  # Chop line until on Sec
            Security = line.rstrip()[0:4].replace("(", " ")
            if Security != 'WEP':
                if Security != 'NONE':
                    Authentication = line[
                                        line.find('(')+1:line.find(')')
                                        ].split("/")[0]
                    PCipher = line[
                                line.find('(')+1:line.find(')')
                                ].split("/")[1]
                    GCipher = line[
                                line.find('(')+1:line.find(')')
                                ].split("/")[2]
                    # print('A:{} P:{} G:{}'.format(
                    #     Authentication, PCipher, GCipher))
                elif Security == 'NONE':
                    Authentication = 'NONE'
                    PCipher = 'NONE'
                    GCipher = 'NONE'
            elif Security == 'WEP':
                Authentication = 'WEP'
                PCipher = 'WEP'
                GCipher = 'WEP'
            if BSSID is not None:
                    ap = AccessPoint("network", SSID, BSSID, Signal, channel,
                                     channel_to_channelwidth(Channel),
                                     channel_to_frequency(Channel),
                                     Authentication, PCipher,
                                     GCipher, NetworkType,
                                     HT, CC, State, Rx, Tx, MAC)
                    results.append(ap)
        return results


def get_scanner(device=""):
    '''
    Identify the platfom of the OS system
    '''
    operating_system = platform.system()
    if operating_system == 'Darwin':
        return OSXRadioScanner(device)
    elif operating_system == 'Linux':
        return LINRadioScanner(device)
    elif operating_system == 'Windows':
        return WINRadioScanner(device)


def print_version():
    '''
    Generate version of the OS system
    '''
    sv = sys.version_info
    py_version = "{}.{}.{}".format(sv.major, sv.minor, sv.micro)
    pass


def main():
    if '-v' in sys.argv or 'version' in sys.argv:
        print_version()
    else:
        device = [x for x in sys.argv[1:] if "-" not in x] or [""]
        device = device[0]
        wifi_scanner = get_scanner(device)
        access_points = wifi_scanner.get_access_points()
        if '-n' in sys.argv:
            print(len(access_points))
        else:
            curStr = json.dumps(access_points[0], indent=4)
            radStr = json.dumps(access_points[1], indent=4)
            # print(radStr)
            # print(curStr)

    dictA = json.loads(curStr)  # Int_Scan # loads Json data to group (k -> v).
    dictB = json.loads(radStr)  # Net_Scan # loads Json data to group (k -> v).

    if len(dictA) != 0:
        # print('cool...')
        curBSSID = str(dictA[0].get('BSSID'))
        i = 0
        for radBSSID in dictB:
            radBSSID = str(dictB[i].get('BSSID'))
            # print(curBSSID)
            # print(radBSSID)
            if curBSSID == radBSSID:
                # print('right...')
                dictB[i].update(dictA[0])
                # dictB[i] = dictA[0]
                mstrScan = json.dumps(dictB, indent=4)  # parse scan data list
                break                                   # to str (Json format).
            elif radStr:
                # print('wrong...')
                pass
            i = i + 1
    else:
        mstrScan = json.dumps(dictB, indent=4)

    print(mstrScan)
    '''
    Database generation process starts from here
    '''
    dictC = json.loads(mstrScan)  # loads Json data to group (k -> v).

    '''
    display list of keys
    '''
    # key = list(dictC[0].keys())
    # print(key)

    '''
    display list of values
    '''
    # value = list(dictC[0].values())
    # print(value)

    '''
    display list of items (k -> v)
    '''
    # item = list(dictC[0].items())
    # print(item)

    # establish Sqlite3 database connection specified by sophos.db file.
    conn = sqlite3.connect("sophos.db", detect_types=sqlite3.PARSE_DECLTYPES |
                           sqlite3.PARSE_COLNAMES)
    c = conn.cursor()

    # delete table mstrScan if it found in sophos.db file.
    c.execute('''DROP TABLE IF EXISTS mstrScan''')

    # create a new table mstrScan if not in sophos.db file.
    c.execute('''CREATE TABLE IF NOT EXISTS mstrScan
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT, Time REAL DEFAULT
                 (datetime('now', 'localtime')), SSID TEXT, BSSID TEXT,
                 Signal TEXT, Channel TEXT, ChannelWidth TEXT, Frequency Text,
                 Authentication TEXT, PCipher TEXT, GCipher TEXT,
                 NetworkType TEXT, HT TEXT, CC TEXT,
                 State TEXT, Rx TEXT, Tx TEXT, MAC TEXT)''')

    # all of the key are below for reference. Total 16 keys.
    '''
    'SSID', 'BSSID', 'Signal', 'Channel', 'ChannelWidth',
    'Frequency', 'Authentication', 'PCipher', 'GCipher', 'NetworkType',
    'HT', 'CC','State', 'Rx', 'Tx', 'MAC'
    '''
    # this loop iterates all the list objects to values (k -> v).
    i = 0
    for item in dictC:
        item = list(dictC[i].items())
        # print(item)
        # insert whole the list object as values in table mstrScan.
        c.execute('''INSERT INTO mstrScan
                     ({0[0]}, {1[0]}, {2[0]}, {3[0]}, {4[0]},
                     {5[0]}, {6[0]}, {7[0]}, {8[0]}, {9[0]},
                     {10[0]}, {11[0]}, {12[0]}, {13[0]},
                     {14[0]}, {15[0]})
                     VALUES ('{0[1]}', '{1[1]}', '{2[1]}',
                     '{3[1]}', '{4[1]}', '{5[1]}', '{6[1]}',
                     '{7[1]}', '{8[1]}', '{9[1]}', '{10[1]}',
                     '{11[1]}', '{12[1]}', '{13[1]}','{14[1]}',
                     '{15[1]}')'''.format(*item))
        i = i + 1
    conn.commit()
    c.close()

if __name__ == '__main__':
    main()
