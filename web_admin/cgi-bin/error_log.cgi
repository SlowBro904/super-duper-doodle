#!/usr/bin/env python3.5
import __init__ as web_admin

from lib.err import ErrCls

errors = ErrCls()

title = "Error log"

# Zebra striped table
header = '''<style>
table {
    border-collapse: collapse;
    width: 100%;
}

th, td {
    text-align: left;
    padding: 8px;
}

tr:nth-child(even){background-color: #f2f2f2}
</style>'''

h1 = title

body = "<table><tr><th>Entry</th></tr>"

# TODO Paginate
# FIXME Test. Not likely to work as errors.log has multiple layers.
for entry in errors.log:
    body += "<tr><td>" + repr(entry) + "</td></tr>"

body += '''</table><br />
<br />'''
body += "<a href='/cgi-bin/home.cgi'>Home</a>"

print(web_admin.get_template() % (title, header, h1, body))