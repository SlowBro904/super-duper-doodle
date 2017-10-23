#!/usr/bin/env python3.5
from sys import path
path.append('../../..')
import __init__ as web_admin

from lib.config import config

device_name = config.conf['DEVICE_NAME']

title = "Service account setup"
header = ""
h1 = title
body = ""

if not config.conf['SERVICE_ACCOUNT_EMAIL']:
    body += "Please enter the email address and password for the " 
    body += device_name + " service.<br />\n"
else:
    body += "Update your email address or password for the " 
    body += device_name + " service.<br />\n"

body += '''If you're not sure what this is please contact customer
service.<br />
<br />
<form action='/cgi-bin/service_account_save.cgi' method='get'>
<table>
<tr><td>Email addresss:</td><td><input type='text' name='email' '''
body += "value='" + config.conf['SERVICE_ACCOUNT_EMAIL'] + "' /></td></tr>"
body += '''<tr><td>Password: </td><td><div align='right'>
<input type='password' name='password1'></div></td></tr>
<tr><td>Repeat password: </td><td><div align='right'>
<input type='password' name='password2'></div></td></tr>
<tr><td></td><td><div align='right'><input type='submit' value='Next'></div>
</td></tr>
</form>
</table>'''

web_admin.show(title, header, h1, body)