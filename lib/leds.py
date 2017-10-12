import threading
from time import sleep
import lib.debugging as debugging
from gpiozero import LED as gpio_LED

# TODO Consider using gpiozero.RGBLED
# TODO Allow blinking

debug = debugging.printmsg

class LEDs(object):
    # These must be hard-coded to prevent a recursion issue where
    # config_class.py cannot load the config file and throws an error.
    # TODO Do I need this now? I don't think I'm running any err in 
    # config_class.py. But I am pretty sure I will be soon. And/or maybe I
    # don't need it now that it's in a separate file?
    good = gpio_LED(10)
    warn = gpio_LED(11)
    err = gpio_LED(12)
    default = {'good': False, 'warn': False, 'err': False}
    
    def LED(self, LED_name = None, default = False):
        '''Shine the LED we specify. If we set a default this is what shines
        even when we turn off the LED. That way for example if we are in a 
        warning state and we run another LED, we want to return to a warning
        state when that is done. Calling default = True will set the last
        called LED as the default.
        '''
        if not LED_name or LED_name is 'default':
            for myLED_name, value in self.default.items():
                if myLED_name is 'good':
                    self.good.value = value
                elif myLED_name is 'warn':
                    self.warn.value = value
                elif myLED_name is 'err':
                    self.err.value = value
            return
        
        if default:
            for myLED_name in self.default:
                if LED_name == myLED_name:
                    self.default[myLED_name] = True
                else:
                    self.default[myLED_name] = False
            debug("self.default: '" + str(self.default) + "'", level = 1)
        
        if LED_name is 'good':
            self.good.value = True
            self.warn.value = False
            self.err.value = False
        elif LED_name is 'warn':
            self.good.value = False
            self.warn.value = True
            self.err.value = False
        elif LED_name is 'err':
            self.good.value = False
            self.warn.value = False
            self.err.value = True
    
# End of class LEDs(object)

leds = LEDs()