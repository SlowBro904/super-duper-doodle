import web_admin

import lib.wifi

title = "Wi-Fi configuration"
h1 = title
body = ""

if lib.wifi.ssid:
    body += "Current Wi-Fi network: " + wifi.ssid + "<br /><br />"

if lib.wifi.ip:
    body += "IP address: " + wifi.ip + "<br /><br />"

body += '''<br />
<form action='/wifi/setup' method='get'>
Connect to a new Wi-Fi network: <select name='ssid'>'''

for this_ssid in lib.wifi.all_ssids:
    if this_ssid == lib.wifi.ssid:
        # Skip my own
        continue
    
    body += "  <option value='" + this_ssid + "'>" + this_ssid + "</option>"

body += '''  <option value='*****N/A*****'>---</option>
  <option value='*****Hidden_network*****'>Hidden network</option>
</select> <input type='submit' value='Next' /></form>'''

print(web_admin.get_template() % (title, header, h1, body))