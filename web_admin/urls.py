def get_web_page_content(path, parameters):
    '''Gets our web page data.
    
    Configure this module for your URLs.
    '''
    if path == '/':
        from home import show
    
    if path.startswith('/wifi/choose_network'):
        from wifi.choose_network import show
    
    if path.startswith('/wifi/setup'):
        from wifi.setup import show
    
    if path.startswith('/wifi/save'):
        from wifi.save import show
    
    if path.startswith('/service_account/setup'):
        from service_account.setup import show
    
    if path.startswith('/service_account/save'):
        from service_account.save import show
    
    if path.startswith('/error_log'):
        from error_log import show
    
    # Ignore anything else
    
    try:
        return show(parameters)
    except NameError:
        # Wrong web page
        return ''