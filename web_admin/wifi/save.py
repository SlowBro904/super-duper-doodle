import web_admin
from sys import exit
from lib.wifi import wifi
from lib.config import config
from lib.reboot import reboot

ssid = None
if 'ssid' in web_admin.params and web_admin.params['ssid']:
    ssid = web_admin.params['ssid']

hidden = False
if 'hidden' in web_admin.params and web_admin.params['hidden'] == 'True':
    hidden = True

password1 = ''
if 'password1' in web_admin.params and web_admin.params['password1']:
    password1 = web_admin.params['password1']

password2 = ''
if 'password2' in web_admin.params and web_admin.params['password2']:
    password2 = web_admin.params['password2']

security_type = ''
if 'security_type' in web_admin.params and web_admin.params['security_type']:
    security_type = web_admin.params['security_type']

title = "Please wait..."
header = ""
h1 = title
body = ""

if not ssid:
    body += '''Missing the SSID<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

if security_type not in ['None', 'WEP', 'WPA', 'WPA2']:
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
    config.update(('WIFI_SSID', ssid), ('WIFI_PASSWORD', password1),
                    ('WIFI_SECURITY_TYPE', security_type))
except:
    body += '''There was some problem writing the config file. Try again or 
    contact technical support.<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    print(web_admin.get_template() % (title, header, h1, body))
    exit()

wifi.connect()

if config.conf['SERVICE_ACCOUNT_EMAIL']:
    body += "<meta http-equiv='refresh' content='10;url=/' />"
else:
    # Service account not setup yet
    body += '''<meta http-equiv='refresh' 
    content='0;url=/service_account/setup' />'''

print(web_admin.get_template() % (title, header, h1, body))