import web_admin
from lib.config import config
from lib.reboot import reboot

email = None
if 'email' in web_admin.params and web_admin.params['email']:
    email = web_admin.params['email']

password1 = ''
if 'password1' in web_admin.params and web_admin.params['password1']:
    password1 = web_admin.params['password1']

password2 = ''
if 'password2' in web_admin.params and web_admin.params['password2']:
    password2 = web_admin.params['password2']


title = "Please wait..."
header = ""
h1 = title
body = ""

if not password1:
    body += '''Missing the password<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    return (title, header, h1, body)

if password1 != password2:
    body += '''Passwords don't match<br />
    <button onclick='window.history.back();'>Go back</button>'''
    
    return (title, header, h1, body)

try:
    config.update(('SERVICE_ACCOUNT_EMAIL', email),
                    ('SERVICE_ACCOUNT_PASSWORD', password1))
except:
    body += '''There was some problem writing the config file. Try again or
    contact technical support.<br />
    <button onclick='window.history.back();'>Go back</button>'''

body += "<meta http-equiv='refresh' content='0;url=/' />"

print(web_admin.get_template() % (title, header, h1, body))