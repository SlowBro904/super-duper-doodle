#!/usr/bin/env python3.5
from sys import path
path.append('../../..')
import __init__ as web_admin

import lib.wifi

title = "Wi-Fi configuration"
header = ""
h1 = title
body = ""

ssid = lib.wifi.ssid()
if ssid:
    body += "Current Wi-Fi network: " + ssid + "<br /><br />\n"

conn_strength = lib.wifi.conn_strength()
if conn_strength and conn_strength is not '0':
    body += "Connection strength: " + conn_strength + "<br /><br />\n"

ip = lib.wifi.ip()
if ip:
    body += "IP address: " + ip + "<br /><br />\n"

body += '''<br />
<form action='/cgi-bin/wifi_setup.cgi' method='get'>
Connect to a new Wi-Fi network: <select name='ssid'>'''

for this_ssid in lib.wifi.all_SSIDs():
    if this_ssid == ssid:
        # Skip my own
        continue
    
    body += "  <option value='" + this_ssid + "'>" + this_ssid + "</option>\n"

# TODO On change submit
body += '''  <option value='*****N/A*****'>---</option>
  <option value='*****Hidden_network*****'>Hidden network</option>
</select> <input type='submit' value='Next' /></form>'''

web_admin.show(title, header, h1, body)