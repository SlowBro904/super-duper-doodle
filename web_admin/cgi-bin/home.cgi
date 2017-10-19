#!/usr/bin/env python3.5
import __init__ as web_admin

import lib.wifi
import lib.debugging
from lib.cloud import cloud
from lib.config import config
from lib.system import SystemCls

device_name = config.conf['DEVICE_NAME']
title = device_name
header = ""
h1 = title
body = ""

system = SystemCls()
serial = system.serial
version = system.version
debug = lib.debugging.printmsg

debug("serial: " + repr(serial), level = 1)
debug("lib.wifi.ssid(): " + repr(lib.wifi.ssid()), level = 1)
debug("lib.wifi.isconnected(): " + repr(lib.wifi.isconnected()), level = 1)

if not lib.wifi.ssid():
    # FIXME Not seen.
    body += '''Let's get started!
    <meta http-equiv='refresh' content='3;url=/cgi-bin/wifi_choose_network.cgi' />'''
elif not lib.wifi.isconnected():
    body += '''I cannot connect to your home router.<br />
    <br />
    <ul>
    <li>Is the <a href='/cgi-bin/wifi_choose_network.cgi'>Wi-Fi configuration</a>
    correct?</li>
    <li>If you are still unable to connect, contact technical support.</li>
    <ul>'''
elif not cloud.isconnected():
    body += "I could not login to the " + device_name + ''' network.<br />
    <br />
    <ul>
    <li>Did your username or password recently change?
    <a href='/cgi-bin/service_account_setup.cgi'>Please update it</a>.</li>
    <li>Is your account still active? Please login to the ''' + device_name
    body += ''' website.</li>
    <li>If you are still unable to connect, contact technical support.</li>
    </ul>'''
else:
    body += '''Connnected to the ''' + device_name + ''' network.<br />
    <br />
    <a href='/cgi-bin/wifi_choose_network.cgi'>Configure Wi-Fi</a><br />
    <br />
    <a href='/cgi-bin/service_account_setup.cgi'>Update your ''' + device_name
    body += ''' service username or password</a>'''

body += '''<br />
<br />
<a href='/cgi-bin/error_log.cgi'>Error log</a><br />
<br />
'''
body += device_name + " version " + version + " | "
body += " Serial number " + serial

print(web_admin.get_template() % (title, header, h1, body))