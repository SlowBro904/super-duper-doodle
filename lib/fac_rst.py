'''Listens to our factory reset switch.

If it's held down more than five seconds do a reset back to factory settings.
'''
import lib.debugging
from time import sleep
from json import dumps
from lib.leds import leds
from lib.err import ErrCls
from gpiozero import Button
from lib.reboot import reboot
from lib.config import config
from os import listdir, remove

errors = ErrCls()

debug = lib.debugging.printmsg
testing = lib.debugging.testing

def _fac_rst_handler():
    ''' Triggered when the reset button is pressed '''
    # FIXME Use the Bash script I wrote for this?
    debug("_fac_rst_handler callback called", level = 1)
    
    # TODO Can I do multiple colors?
    leds.LED('warn')
    sleep(5)
    
    fac_rst_pin = config.conf['FACTORY_RESET_PIN']
    fac_rst_pin_lsnr = Button(fac_rst_pin)
    if fac_rst_pin_lsnr.value is not True:
        return
    
    debug("Proceeding to factory reset", level = 1)
    
    leds.LED('err')
    
    #try:
    config.reset_to_defaults()
    #except:
    #    # FIXME except what?
    #    error = ("Could not reset to factory defaults.",
    #                "('factory_reset.py', 'fac_rst_handler')"
    #    errors.err(error)
    
    # Also delete local data files
    for data_path in ['/SmartBird/data', '/SmartBird/data']:
        for file in listdir(data_path):
            #try:
            remove(data_path + '/' + file)
            #except OSError:
            #    # Ignore if any issue at all
            #    pass
    
    # Create a flag file to notify cloud.get_data_updates to fetch all data
    # files
    get_all_data_files_flag = '/SmartBird/get_all_data_files.json'
    #try:
    with open(get_all_data_files_flag, 'w') as f:
        f.write(dumps(True))
    #except:
    #    # Ignore errors
    #    pass
    
    if testing:
        print("***Pretending to reboot***")
    else:
        reboot(delay = 3)


# Setup our listener
fac_rst_pin = config.conf['FACTORY_RESET_PIN']
debug("fac_rst_pin: '" + str(fac_rst_pin) + "'", level = 1)

#try:
fac_rst_pin_lsnr = Button(fac_rst_pin)
fac_rst_pin_lsnr.when_pressed = _fac_rst_handler
#except:
#    errors.err("Cannot listen for factory reset button presses.",
#                    "('factory_reset.py', 'main')")