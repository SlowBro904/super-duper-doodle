from sys import argv
import lib.debugging
from json import loads
from lib.cmd import cmd
from os import chdir, path
from lib.config import config

debug = lib.debugging.printmsg

# Change to the directory this script is running in
chdir(path.dirname(path.abspath(argv[0])))

class SystemCls(object):
    @property
    def version(self):
        '''Sets the version number variable based on the version number file'''
        # TODO Also get the sys.* version numbers
        # https://docs.pycom.io/pycom_esp32/library/sys.html
        
        try:
            return self._version
        except AttributeError:
            # FIXME Does the ConfigCls have the ability to add new config
            # items? And if so how do I intend to add them? Some one-off
            # startup script.
            with open(config.conf['VERSION_NUMBER_FILE']) as f:
                self._version = loads(f.read())
        #except:
        #    error = "Cannot get our version number. ('system.py', 'version')"
        #    self.err.error(error)
        return self._version
    
    
    @property
    def serial(self):
        ''' Sets our serial number variable based on the system's unique ID '''
        try:
            return self._serial
        except AttributeError:
            with open('/proc/cpuinfo') as f:
                for row in f.readlines():
                    if row.startswith('Serial'):
                        self._serial = row.split()[2].strip('0')
                        break
        return self._serial
    
    
    @property
    def attached_devices(self):
        '''Looks for i2c addresses for devices we certify and appends to a set
        of attached devices.
        
        Ignores any non-certified hardware.
        '''        
        try:
            self._attached_devices
        except AttributeError:
            self._attached_devices = set()
            
            # We always have at least one door opener, which does not use I2C
            self._attached_devices.add('door')
            
            # TODO Implement I2C devices here
            
        return list(self._attached_devices)