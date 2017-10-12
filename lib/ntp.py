import lib.debugging
from lib.cmd import cmd
from re import search as re_search

debug = lib.debugging.printmsg

def status():
    '''Returns the status of NTP synchronization'''
    synched = False
    for row in cmd('timedatectl status')[0].split('\n'):
        debug("row: " + repr(row), level = 1)
        match = re_search(r'^NTP synchronized: (.*)', row)
        if match:
            if match.group(1) == 'yes':
                synched = True
                break
    return synched