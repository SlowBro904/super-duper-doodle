import lib.debugging
from lib.err import ErrCls
from lib.config import config
from re import search as re_search
from urllib.parse import urlparse, parse_qs

err = ErrCls()
debug = lib.debugging.printmsg

def get_template():
    '''Returns our template as a list'''
    #try:
    template = list()
    with open(config.conf['WEB_ADMIN_TEMPLATE_FILE']) as f:
        for row in f.read():
            template.append(row)
    
    template = '\n'.join(template)
    #except OSError:
    #    warning = ("Could not load the web admin template.",
    #                " ('web_admin/__init__.py', '_daemon')")
    #    err.warning(warning)
    #    return False
    return template


def get_params(request):
    '''Given a request, returns the path and parameters'''
    debug("request: " + repr(request))
    
    path = urlparse(request).path
    params = parse_qs(urlparse(request).query)
    
    debug("path: " + repr(path))
    debug("params: " + repr(params))
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


def serve():
    '''Actual web content'''
    from urls import get_web_page_content
    
    path, params = get_params(request)
    
    web_page_content = get_web_page_content(path, params)
    
    if web_page_content:
        # Load web_page_content into our template
        web_page_content = get_template() % (web_page_content)
        
        # FIXME Needed?
        data = 'HTTP/1.0 200 OK\r\n'
        data += 'Content-type: text/html\r\n'
        data += 'Content-length: ' + str(len(web_page_content)) + '\r\n'
        data += '\r\n'
        data += web_page_content
        
        return data