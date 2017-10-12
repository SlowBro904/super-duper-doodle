import lib.debugging
from lib.err import ErrCls
from importlib import import_module

errors = ErrCls()
debug = lib.debugging.printmsg

class DeviceRoutine(object):
    def __init__(self, device):
        '''This sets up an object for the routines of a particular device'''
        self.module = import_module('lib.device_routines.' + device)
        debug("self.module: " + repr(self.module))
    
    
    def run(self, cmd, args = None):
        '''This runs a command for a particular device.'''
        routine = getattr(self.module, cmd)
        
        #try:
        return routine(args)
        #except:
        #    warning = ("Could not run command " + command + " on device ",
        #                device + " with these arguments: '" + str(args),
        #                "' ('device_routines/__init__.py','run')")
        #    err.warning(warning)
        #    return False