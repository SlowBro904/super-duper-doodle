import lib.wifi
import web_admin
from lib.cloud import cloud
from lib.config import config
# TODO Rename SystemCls to be consistent
from lib.system import System

device_name = config.conf['DEVICE_NAME']
title = device_name
header = ""
h1 = title
body = ""

serial = System().serial
version = System().version

if not lib.wifi.ssid:
    body += '''Let's get started!
    <script>window.location.href = '/wifi/choose_network';</script>'''
elif not lib.wifi.isconnected():
    body += '''I cannot connect to your home router.<br />
    <br />
    <ul>
    <li>Is the <a href='/wifi/choose_network'>Wi-Fi configuration</a>
    correct?</li>
    <li>If you are still unable to connect, contact technical support.</li>
    <ul>'''
elif not cloud.can_login():
    body += "I could not login to the " + device_name + ''' network.<br />
    <br />
    <ul>
    <li>Did your username or password recently change?
    <a href='/service_account/setup'>Please update it</a>.</li>
    <li>Is your account still active? Please login to the ''' + device_name
    + ''' website.</li>
    <li>If you are still unable to connect, contact technical support.</li>
    </ul>'''
else:
    body += '''Connnected to the ''' + device_name + ''' network.<br />
    <br />
    <a href='/wifi/choose_network'>Configure Wi-Fi</a><br />
    <br />
    <a href='/service_account/setup'>Update your ''' + device_name 
    + ''' service username or password</a>'''

body += '''<br />
<br />
<a href='/error_log'>Error log</a><br />
<br />
'''
body += device_name + " software version " + version + " | "
body += " Serial number " + serial

print(web_admin.get_template() % (title, header, h1, body))