#!/usr/bin/env python3.5
import test_suite
import lib.fac_rst
from time import sleep
from os import rename, remove
from lib.config import config

good = test_suite.good

rename('/SmartBird/config/config.json', '/SmartBird/config/config.good.json')
with open('/SmartBird/config/config.good.json') as g:
    with open('/SmartBird/config/config.json', 'w') as c:
        c.write(g.read())

try:
    test_str = 'Config file updated'
    config.update({"XYZ": test_str})
    assert config.conf["XYZ"] == test_str, "config.update()"
    good("config.update()")
    # FIXME Can't on() a button. Maybe use a source to turn this on?
    lib.fac_rst.fac_rst_pin_lsnr.on()
    # FIXME Automate
    #print("Sleeping four seconds...")
    #sleep(4)
    #fac_rst.fac_rst_pin_lsnr.off()
    #assert config.conf["XYZ"] == test_str, "Did fac_rst before five seconds"
    #good("Didn't reset at four seconds")
    #fac_rst.fac_rst_pin_lsnr.on()
    print("Sleeping twenty seconds. Hold the reset button for five seconds.")
    sleep(20)
    #fac_rst.fac_rst_pin_lsnr.off()
    assert config.conf["XYZ"] == None, "fac_rst failed"
    good("fac_rst")
finally:
    # Always restore our good config
    with open('/SmartBird/config/config.good.json') as g:
        with open('/SmartBird/config/config.json', 'w') as c:
            c.write(g.read())
    remove('/SmartBird/config/config.good.json')