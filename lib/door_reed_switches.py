import lib.debugging
from lib.err import ErrCls
from gpiozero import Button
from lib.config import config

def status():
    '''Tells whether the door is in the up or down position'''
    debug = lib.debugging.printmsg
    
    errors = ErrCls()
    
    up_pin = config.conf['DOOR_REED_UP_PIN']
    dn_pin = config.conf['DOOR_REED_DN_PIN']
    
    up_btn = Button(up_pin)
    dn_btn = Button(dn_pin)
    
    up = up_btn.value
    dn = dn_btn.value
    
    # FIXME With nothing plugged in they default to down. Not sure why.
    status = 'between'
    if dn and not up:
        status = 'dn'
    elif not dn and up:
        status = 'up'
    elif up and dn:
        errors.err('Door reed switch malfunction.')
    
    debug("status: '" + str(status) + "'", level = 1)
    return status