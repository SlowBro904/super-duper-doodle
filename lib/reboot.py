import lib.debugging
from time import sleep
from lib.cmd import cmd
from threading import Thread

debug = lib.debugging.printmsg
testing = lib.debugging.testing

def reboot(delay = 0, boot_cause = None):
    '''Reboots the device.
    
    Takes an optional delay value in seconds. 

    A good usage of the delay would be to allow for the web server to show HTML
    content to the browser.
    '''
    t = Thread(target = _reboot, args = (delay,))
    t.start()

def _reboot(delay):
    '''This is the actual reboot command.
    
    Not recommended you call this directly. Use reboot() instead.
    '''
    # TODO Do I need to loop on delay count and sleep(1) inside?
    sleep(delay)
    
    if testing:
        # TODO Return or set some value for testing
        debug("Simulating reboot")
    else:
        cmd('reboot')