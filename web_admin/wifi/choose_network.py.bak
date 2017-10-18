#!/usr/bin/env python3.5
from sys import path
path.append('../..')
import web_admin

import lib.wifi

title = "Wi-Fi configuration"
header = ""
h1 = title
body = ""

if lib.wifi.ssid():
    body += "Current Wi-Fi network: " + lib.wifi.ssid() + "<br /><br />\n"

if lib.wifi.ip():
    body += "IP address: " + lib.wifi.ip() + "<br /><br />\n"

body += '''<br />
<form action='/cgi-bin/wifi/setup.py' method='get'>
Connect to a new Wi-Fi network: <select name='ssid'>'''

for this_ssid in lib.wifi.all_SSIDs():
    if this_ssid == lib.wifi.ssid():
        # Skip my own
        continue
    
    body += "  <option value='" + this_ssid + "'>" + this_ssid + "</option>\n"

# TODO On change submit
body += '''  <option value='*****N/A*****'>---</option>
  <option value='*****Hidden_network*****'>Hidden network</option>
</select> <input type='submit' value='Next' /></form>'''

print(web_admin.get_template() % (title, header, h1, body))