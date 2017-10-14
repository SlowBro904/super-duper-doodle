import web_admin
from lib.err import ErrCls

errors = Err()

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

body = "<table>"

# TODO Paginate
for entry in errors.log:
    body += "<tr><td>" + entry + "</td></tr>"

body += '''</table><br />
<br />'''
body += "<a href='/'>Home</a>"

print(web_admin.get_template() % (title, header, h1, body))