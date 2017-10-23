#!/usr/bin/env python3.5
from sys import path
path.append('../../..')
import __init__ as web_admin

import lib.wifi
from lib.config import config

title = "Connect to a new Wi-Fi network"

ssid = None
if 'ssid' in web_admin.params and web_admin.params['ssid']:
    ssid = web_admin.params['ssid'].value

if ssid == '*****Hidden_network*****':
    ssid = None
    hidden = True

header = '''
<script>
function show_passwords() {
    document.getElementById('password1').style.display = "table-row";
    document.getElementById('password2').style.display = "table-row";
}
function hide_passwords() {
    document.getElementById('password1').style.display = "none";
    document.getElementById('password2').style.display = "none";
}
</script>'''

h1 = title

body = '''<form action='/cgi-bin/wifi_save.cgi' method='get'>
<table>'''

sec_type = 'None'

if ssid:
    sec_type = lib.wifi.AP_sec_type(ssid)
    
    body += '''<tr><td>Network name (ssid): </td><td><div align='right'>'''
    body += ssid + "</div></td></tr>\n"
    body += "<input type='hidden' name='ssid' value='" + ssid + "' />\n"
    body += "<input type='hidden' name='sec_type' value='" + str(sec_type)
    body += "' />\n"
else:
    body += "<tr><td>Network name (ssid):</td><td><div align='right'>\n"
    body += "<input type='text' name='ssid' /></div></td></tr>\n"

    if hidden:
        body += "<input type='hidden' name='hidden' value='True' />\n"
    else:
        body += '''<tr><td>&nbsp;</td>
        <td><label><input type='checkbox' name='hidden' value='True'>Hidden
        </label>
        </td></tr>'''
    
    body += '''<tr><td>Security type: </td><td>
    <input type='radio' name='sec_type' value='None' 
        onclick='hide_passwords();'>None</input>
    <input type='radio' name='sec_type' value='wep'  
        onclick='show_passwords();'>WEP</input>
    <input type='radio' name='sec_type' value='wpa'  
        onclick='show_passwords();'>WPA</input>
    <input type='radio' name='sec_type' value='wpa2' 
        onclick='show_passwords();'>WPA2</input>
    </td></tr>'''

body += '''<tr id='password1' style='display:none'><td>Password: </td><td>
<div align='right'><input type='password' name='password1'></div></td></tr>
<tr id='password2' style='display:none'><td>Repeat password: </td><td>
<div align='right'><input type='password' name='password2'></div></td></tr>
<tr><td></td><td></td></tr>
<tr><td></td><td><div align='right'><input type='submit' value='Next'>
</div></td></tr>
</table>
</form>'''

if sec_type != 'None':
    body += '''<script>show_passwords();</script>'''

web_admin.show(title, header, h1, body)