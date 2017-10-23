#!/usr/bin/env python3.5
import test_suite
from json import loads
from os import rename, remove
from lib.config_class import Config

config = Config('/SmartBird/config/config.json',
                '/SmartBird/config/defaults.json')

test_str = 'Config file updated'

good = test_suite.good

try:
    config.conf['XYZ']
except (NameError, TypeError):
    raise AssertionError("Cannot read the config")

good("config.conf['XYZ'] at the start of the test: '" +
    str(config.conf['XYZ']) + "'")

config.update({'XYZ': test_str})
assert config.conf['XYZ'] == test_str, "Cannot update the config"
good("config.conf['XYZ'] after update: '" + str(config.conf['XYZ']) + "'")

check = "Wrote changed config"
with open('/SmartBird/config/config.json') as f:
    myconfig = loads(f.read())
    assert myconfig['XYZ'] == test_str, check
good(check)

config.update({'XYZ': None})
assert config.conf['XYZ'] is None, "Did not empty the XYZ config"
good("Emptied the XYZ config")

del(config.conf['XYZ'])
config.conf = config.load_config()
assert config.conf['XYZ'] is None, "Cannot load the config from flash"
good("Loaded the config from flash")

config.update({'Nonexistant': None})

check = "Should not have updated nonexistant config option 'Nonexistant'"
assert 'Nonexistant' not in config.conf, check
good(check)

try:
    rename('/SmartBird/config/config.json',
            '/SmartBird/config/config.good.json')
except OSError:
    # TODO Entire error is OSError: error renaming file
    # '/SmartBird/config.json' to '/SmartBird/config.good.json'
    debug("Couldn't rename config.json to config.good.json", level = 1)
    pass

with open('/SmartBird/config/config.good.json') as g:
    with open('/SmartBird/config/config.json', 'w') as c:
        c.write(g.read())

try:
    config.update({"XYZ": test_str})
    assert config.conf["XYZ"] == test_str, "config.update()"
    good("config.update()")
    config.reset_to_defaults()
    assert config.conf["XYZ"] == None, "fac_rst failed"
    good("fac_rst")
finally:
    # Whether we error or succeed, restore our config
    #print("[DEBUG] Restoring the config")
    with open('/SmartBird/config/config.good.json') as g:
        with open('/SmartBird/config/config.json', 'w') as c:
            c.write(g.read())
    remove('/SmartBird/config/config.good.json')

config.conf = config.load_config()
#print("[DEBUG] test_config.py config.conf: '" + str(config.conf) + "'")
assert config.conf['XYZ'] == None, "Cannot load the config from flash"
good("Loaded the config from flash")

good("config.conf['XYZ'] at the end of the test: '" +
    str(config.conf['XYZ']) + "'")

# FIXME Re-create defaults.json