#!/usr/bin/env python3.5
from sys import path
path.append('../../..')
import __init__ as web_admin

import lib.wifi
from sys import exit
from time import sleep
from lib.config import config
from lib.reboot import reboot

ssid = None
if 'ssid' in web_admin.params and web_admin.params['ssid']:
    ssid = web_admin.params['ssid'].value

hidden = False
if 'hidden' in web_admin.params and web_admin.params['hidden'] == 'True':
    hidden = True

password1 = ''
if 'password1' in web_admin.params and web_admin.params['password1']:
    password1 = web_admin.params['password1'].value

password2 = ''
if 'password2' in web_admin.params and web_admin.params['password2']:
    password2 = web_admin.params['password2'].value

sec_type = ''
if 'sec_type' in web_admin.params and web_admin.params['sec_type']:
    sec_type = web_admin.params['sec_type'].value

title = "Saving..."
header = ""
h1 = title
body = ""

if not ssid:
    body += '''Missing the SSID<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

if sec_type not in ['None', 'wep', 'wpa', 'wpa2']:
    body += '''Missing the security type<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

# The password might be empty so don't check that it was passed, only that
# it matches
if password1 != password2:
    body += '''Passwords don't match<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

try:
    lib.wifi.config(ssid, password1, sec_type, hidden)
except:
    lib.wifi.defaults()
    body += '''There was some problem saving the config. Try again or 
    contact technical support.<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

if config.conf['SERVICE_ACCOUNT_EMAIL']:
    body += "<meta http-equiv='refresh' content='10;url=/cgi-bin/home.cgi' />\n"
else:
    # Service account not setup yet
    body += '''<meta http-equiv='refresh' 
    content='0;url=/cgi-bin/service_account_setup.cgi' />'''

sleep(30)
lib.wifi.connect()

print(web_admin.get_template() % (title, header, h1, body))