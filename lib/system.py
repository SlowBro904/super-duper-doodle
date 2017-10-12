from json import loads
from lib.cmd import cmd
from lib.config import config

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
            self._serial = cmd('lib/get_serial.sh')[0]
        return self._serial
    
    
    @property
    def attached_devices(self):
        '''Looks for i2c addresses for devices we certify and appends to a set
        of attached devices.
        
        Ignores any non-certified hardware.
        '''        
        try:
            return self._attached_devices
        except AttributeError:
            self._attached_devices = set()
            
            # We always have at least one door opener, which does not use I2C
            self._attached_devices.add('door')
            
            # TODO Implement I2C devices here
            
        return self._attached_devices