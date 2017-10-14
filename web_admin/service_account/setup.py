import web_admin
from lib.config import config

device_name = config.conf['DEVICE_NAME']

title = "Service account setup"
header = ""
h1 = title
body = ""

if not config.conf['SERVICE_ACCOUNT_EMAIL']:
    body += "Please enter the email address and password for the " 
    body += device_name + " service.<br />"
else:
    body += "Update your email address or password for the " 
    body += device_name + " service.<br />"

body += '''If you're not sure what this is please contact customer
service.<br />
<br />
<form action='/service_account_save' method='get'>
<table>
<tr><td>Email addresss:</td><td><input type='text' name='email' />''' 
body += config.conf['SERVICE_ACCOUNT_EMAIL'] + '''</td></tr>
<tr><td>Password: </td><td><div align='right'>
<input type='password' name='password1'></div></td></tr>
<tr><td>Repeat password: </td><td><div align='right'>
<input type='password' name='password2'></div></td></tr>
<tr><td></td><td><div align='right'><input type='submit' value='Next'></div>
</td></tr>
</form>
</table>'''

print(web_admin.get_template() % (title, header, h1, body))