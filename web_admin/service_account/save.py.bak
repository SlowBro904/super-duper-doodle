#!/usr/bin/env python3.5
from sys import path
path.append('../..')
import web_admin

from sys import exit
from lib.config import config

email = None
if 'email' in web_admin.params and web_admin.params['email']:
    email = web_admin.params['email'].value

password1 = ''
if 'password1' in web_admin.params and web_admin.params['password1']:
    password1 = web_admin.params['password1'].value

password2 = ''
if 'password2' in web_admin.params and web_admin.params['password2']:
    password2 = web_admin.params['password2'].value


title = "Please wait..."
header = ""
h1 = title
body = ""

if not password1:
    body += '''Missing the password<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

if password1 != password2:
    body += '''Passwords don't match<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

try:
    config.update({'SERVICE_ACCOUNT_EMAIL': email,
                   'SERVICE_ACCOUNT_PASSWORD': password1})
except:
    body += '''There was some problem writing the config file. Try again or
    contact technical support.<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

body += "<meta http-equiv='refresh' content='0;url=/cgi-bin/home.py' />"

print(web_admin.get_template() % (title, header, h1, body))