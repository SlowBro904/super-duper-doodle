#!/usr/bin/env python3.5
import test_suite

import web_admin
from lib.config import config

good = test_suite.good

check = 'get_params()'
url = 'http://1.1.1.1/test?test=test'
assert web_admin.get_params(url) == ('/test', {'test': ['test']}), check
good(check)

check = 'get_template()'
template = list()
with open(config.conf['WEB_ADMIN_TEMPLATE_FILE']) as f:
    for row in f.read():
        template.append(row)
template = '\n'.join(template)
assert template == web_admin.get_template(), check
good(check)

check = 'status()'
# Just making sure it returns True or False
assert isinstance(web_admin.status(), bool), check
good(check)