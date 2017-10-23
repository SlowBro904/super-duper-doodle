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

body = "<table><tr><th>Date/time</th><th>Type</th><th>Log entry</th></tr>"

# TODO Paginate
# FIXME Test. Not likely to work as errors.log has multiple layers.
# log_entry = (timestamp, mytype, {'message': msg})
for entry in errors.log:
    timestamp = entry[0]
    mytype = entry[1]
    if mytype is not 'exception':
        message = entry[2]['message']
    else:
        try:
            myfile = entry[2]['file']
        except KeyError:
            myfile = None
        
        try:
            myclass = entry[2]['class']
        except KeyError:
            myclass = None
        
        try:
            myfunc = entry[2]['func']
        except KeyError:
            myfunc = None
        
        try:
            myaction = entry[2]['action']
        except KeyError:
            myaction = None
        
        try:
            myexc_type = entry[2]['exc_type']
        except KeyError:
            myexc_type = None
        
        try:
            myerror = entry[2]['error']
        except KeyError:
            myerror = None

        message = list()
        for myvalue in [myfile, myclass, myfunc, myaction, myexec_type, 
                        myerror]:
            if myvalue:
                message.append(myvalue)
        
        # Convert to pipe-delimited string
        message = ' | '.join(message)
    
    body += "<tr><td>" + timestamp + "</td><td>" + mytype + "</td><td>"
    body += message + "</td></tr>"

body += '''</table><br />
<br />'''
body += "<a href='/cgi-bin/home.cgi'>Home</a>"

web_admin.show(title, header, h1, body)