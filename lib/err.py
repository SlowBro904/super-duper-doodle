import sys
import lib.debugging
from os import remove
from time import sleep
from lib.leds import leds
from datetime import datetime

debug = lib.debugging.printmsg
testing = lib.debugging.testing

class ErrCls(object):
    # This is a global class log. All instances will log here.
    log = list()
    
    
    def msg(self, mytype, msg):
        '''Adds a message of a certain type to the ongoing in-memory log
        '''
        debug("err.py msg() msg: '" + str(msg) + "'", level = 1)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = (timestamp, mytype, {'message': msg})
        ErrCls.log.append(log_entry)
        # TODO Reimplement some kind of datastore in case I cannot upload and
        # get rebooted
    
    
    def warn(self, msg):
        '''Turns on the warning LED, adds the warning to the log set, and saves
        it to the data_store
        '''
        self.msg('warning', msg)
        leds.LED('warn', default = True)
    
    
    def err(self, msg):
        '''Things got real bad. Stop everything.'''
        self.msg('error', msg)
        
        # FIXME Is that enough time? Maybe wait for a completion flag. But time
        # that out.
        sleep(3)
        
        # Steady red LED
        leds.LED('err', default = True)
        
        # FIXME Do what now? This is where I deepsleep'd before
    
    
    def exc(self, args = None):
        '''Log uncaught exceptions.

        args is a dict that can optionally include:
        'file': The file name such as __file__
        'class': The class name such as self.__class__.__name__
        'func': The function we are in such as '__init__'
        'action': A human-readable string describing the action we were taking
            such as "Testing exception logging"
        '''
                
        # TODO Start to use sys.print_exception() and sys.excepthook instead
        # TODO Also optionally allow the exception to flow through to stderr
        if args:
            content = args
        else:
            content = dict()
        
        content['exc_type'] = str(sys.exc_info()[0])
        content['error'] = str(sys.exc_info()[1]).strip()
        
        # TODO And what about the exc_num like in OSError? For now,
        # investigate by hand and later, by allowing an exception argument 
        # to this module.
        
        self.msg('exception', content)
        
        if not testing:
            sys.exit(1)