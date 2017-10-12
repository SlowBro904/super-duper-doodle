#!/usr/bin/env python3.5
import test_suite

import lib.wifi
from lib.config import config

good = test_suite.good

assert lib.wifi.ssid == config.conf['WIFI_SSID'], "WIFI_SSID"
good("WIFI_SSID")

try:
    ip = config.conf['WEB_ADMIN_IP']
except KeyError:
    ip = None
assert ip is not None, "WEB_ADMIN_IP"
good("WEB_ADMIN_IP")

try:
    subnet_mask = config.conf['WEB_ADMIN_SUBNET_MASK']
except KeyError:
    subnet_mask = None
assert subnet_mask is not None, "WEB_ADMIN_SUBNET_MASK"
good("WEB_ADMIN_SUBNET_MASK")

try:
    gateway = config.conf['WEB_ADMIN_NETWORK_GATEWAY']
except KeyError:
    gateway = None
assert gateway is not None, "WEB_ADMIN_NETWORK_GATEWAY"
good("WEB_ADMIN_NETWORK_GATEWAY")

try:
    DNS_server = config.conf['WEB_ADMIN_DNS_SERVER']
except KeyError:
    DNS_server = None
assert DNS_server is not None, "WEB_ADMIN_DNS_SERVER"
good("WEB_ADMIN_DNS_SERVER")

# FIXME Create a test for WEP in a separate file so I can switch the network
lib.wifi.config(ssid = "Be:my:guest", passphrase = "Guest:my:be",
    enc_type = "WPA", hidden = True)
lib.wifi.connect()
assert lib.wifi.isconnected() is True, "isconnected()"
good("isconnected()")

assert isinstance(lib.wifi.ip(), str), "Cannot get IP"
good("Got the IP")

assert lib.wifi.AP_sec_type('xfinitywifi') is None, "get_AP_sec_type()"
good("get_AP_sec_type()")

assert len(lib.wifi.all_SSIDs()) > 0, "all_SSIDs"
good("all_SSIDs")

assert len(lib.wifi.all_APs()) >= len(lib.wifi.all_SSIDs()), "all_SSIDs list not right"
good("all_SSIDs list correct length")

conn_strength = lib.wifi.conn_strength
if conn_strength:
    assert conn_strength < 0, "conn_strength: '" + str(conn_strength) + "'"
    good("conn_strength: '") + str(conn_strength) + "'"