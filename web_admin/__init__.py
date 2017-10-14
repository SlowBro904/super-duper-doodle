#!/usr/bin/env python3.5
from sys import path
path.append('/SmartBird')

import cgi
# FIXME Remove for prod
import cgitb; cgitb.enable()
import lib.debugging
from lib.err import ErrCls
from lib.config import config
from re import search as re_search
from urllib.parse import urlparse, parse_qs

err = ErrCls()
debug = lib.debugging.printmsg

def get_template():
    '''Returns our template as a string'''
    #try:
    with open(config.conf['WEB_ADMIN_TEMPLATE_FILE']) as f:
        template = f.readlines()
    
    #except OSError:
    #    warning = ("Could not load the web admin template.",
    #                " ('web_admin/__init__.py', '_daemon')")
    #    err.warning(warning)
    #    return False
    return template


def get_params(request):
    '''Given a request, returns the path and parameters'''
    debug("request: " + repr(request), level = 1)
    
    params = parse_qs(urlparse(request).query)
    
    debug("params: " + repr(params), level = 1)
    return (path, params)


def start():
    '''Start the web admin interface'''
    # FIXME Start web server
    pass


def stop():
    '''Stop the web admin interface'''
    # FIXME Stop web server
    pass


def status():
    '''Status of the web server'''
    # FIXME Finish
    return True


# Boilerplate for all web pages
# FIXME Where do I get url? CGI methinks...
params = get_params(url)

# FIXME Needed?
print('HTTP/1.0 200 OK\r\n')
print('Content-type: text/html\r\n')
# FIXME Needed?
#print('Content-length: ' + str(len(web_page_content)) + '\r\n')
print('\r\n')
