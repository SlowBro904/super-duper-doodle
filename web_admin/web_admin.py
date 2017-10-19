#!/usr/bin/env python3.5
from http.server import HTTPServer, CGIHTTPRequestHandler

class Handler(CGIHTTPRequestHandler):
    cgi_directories = ['/cgi-bin']

httpd = HTTPServer(('', 80), Handler)
httpd.serve_forever()