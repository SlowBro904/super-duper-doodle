#!/usr/bin/env python3.5
import test_suite

import lib.wifi
import lib.debugging
from json import loads
from lib.cmd import cmd
from lib.config import config

debug = lib.debugging.printmsg

good = test_suite.good

lib.wifi.defaults()
check = "defaults()"
conf_md5 = cmd("md5sum " + lib.wifi.conf_file)[0].split()[0]
debug("conf_md5: " + repr(conf_md5), level = 1)
defaults_md5 = cmd("md5sum " + lib.wifi.conf_file + ".defaults")[0].split()[0]
debug("defaults_md5: " + repr(defaults_md5), level = 1)
assert conf_md5 == defaults_md5, check
good(check)

# FIXME Create a test for WEP in a separate file so I can switch the network
# FIXME Also a config for a hidden network
with open('/root/wifi.json') as f:
    ssid, password = loads(f.read())

lib.wifi.config(ssid = ssid, password = password, enc_type = "WPA")
lib.wifi.connect()

assert lib.wifi.isconnected() is True, "isconnected()"
good("isconnected()")

debug("lib.wifi.ssid(): " + repr(lib.wifi.ssid()), level = 1)
assert lib.wifi.ssid() == "ThisNetworkIsMonitored!2", "WIFI_SSID"
good("WIFI_SSID")

check = "IP"
assert isinstance(lib.wifi.ip(), str), check
good(check)

assert lib.wifi.AP_sec_type('xfinitywifi') is None, "get_AP_sec_type()"
good("get_AP_sec_type()")

assert len(lib.wifi.all_SSIDs()) > 0, "all_SSIDs"
good("all_SSIDs")

debug("len(lib.wifi.all_APs()): " + repr(len(lib.wifi.all_APs())), level = 1)
debug("lib.wifi.all_APs(): " + repr(lib.wifi.all_APs()), level = 0)
debug("len(lib.wifi.all_SSIDs()): " + repr(len(lib.wifi.all_SSIDs())), level = 1)
debug("lib.wifi.all_SSIDs(): " + repr(lib.wifi.all_SSIDs()), level = 0)
assert len(lib.wifi.all_APs()) >= len(lib.wifi.all_SSIDs()), "all_SSIDs list not right"
good("all_SSIDs list correct length")

conn_strength = int(lib.wifi.conn_strength())
if conn_strength:
    assert conn_strength > 0, "conn_strength: '" + str(conn_strength) + "'"
    good("conn_strength: " + repr(conn_strength))

