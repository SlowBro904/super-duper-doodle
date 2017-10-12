'''A config module which can be imported into other modules but which is 
specific to this device.

Improves performance by avoiding reloading the config file every time it's
imported.
'''
# TODO I think I can just integrate the Config() class here since the file 
# names won't change
from lib.config_class import Config

# FIXME Move exception testing for this situation into err
#try:
config = Config(config_file = '/SmartBird/config/config.json',
                defaults_file = '/SmartBird/config/defaults.json')
#except:
#    error = "Could not load the config. ('config.py', 'main')"
#    #err.error(error)