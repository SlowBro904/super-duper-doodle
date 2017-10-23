import lib.debugging
from time import sleep
from gpiozero import Motor
from lib.config import config
import lib.door_reed_switches
from time import time as current_time
from sys import setrecursionlimit, getrecursionlimit

debug = lib.debugging.printmsg
default_recursion_limit = getrecursionlimit()

up_pin = config.conf['MOTOR_UP_PIN']
dn_pin = config.conf['MOTOR_DN_PIN']
current_pin = config.conf['MOTOR_CURRENT_PIN']
low_current = config.conf['MOTOR_LOW_CURRENT']
high_current = config.conf['MOTOR_HIGH_CURRENT']
check_interval = config.conf['MOTOR_CHECK_INTERVAL']

motor = Motor(up_pin, dn_pin)

def operate(direction):
    '''Takes 'up' or 'dn' and moves the door in that direction'''
    motor_obj = MotorCls()
    motor_obj.run(direction)


class MotorCls(object):
    timeout = config.conf['MOTOR_TIMEOUT']
    
    
    def __init__(self, timeout = None, check_interval = None):
        '''Sets up the motor object'''
        if timeout:
            self.timeout = timeout
        
        if check_interval:
            self.check_interval = check_interval
        
        self.stop()
    
    
    def run(self, direction, timeout = None):
        '''Starts the motor in the requested direction.
        
        It will stop on its own based on the door reed switces.
        '''
        if not timeout:
            timeout = self.timeout
        
        if direction == 'up':
            debug("door.py run() Direction is up.", level = 0)
            debug("Before setting:", level = 1)
            debug("motor.value: '" + str(motor.value) + "'", level = 1)
            motor.forward()
            debug("After setting:", level = 1)
            debug("motor.value: '" + str(motor.value) + "'", level = 1)
        elif direction == 'dn':
            debug("door.py run() Direction is dn.", level = 0)
            debug("Before setting:", level = 1)
            debug("motor.value: '" + str(motor.value) + "'", level = 1)
            motor.backward()
            debug("After setting:", level = 1)
            debug("motor.value: '" + str(motor.value) + "'", level = 1)
        else:
            motor.stop()
        
        start_time = current_time()
        
        while True:
            if current_time() >= (start_time + timeout):
                debug("door.py run() Motor timed out", level = 0)
                self.stop()
                return False
            
            # If the status shows we are completely in the direction requested
            if lib.door_reed_switches.status() == direction:
                debug("door.py run() door_reed_switches.status()==direction." +
                        "Stopping.", level = 0)
                debug("motor.value: '" + str(motor.value) + "'", level = 1)
                self.stop()
                return True
            
            # Constantly monitor the current and if it is out of range stop,
            # reverse for three seconds, then try again
            if not low_current < self.current < high_current:
                debug("We are outside of current range, reversing.", level = 1)
                self.stop()
                
                if direction == 'up':
                    reverse = 'dn'
                else:
                    reverse = 'up'
                
                try:
                    # Don't keep reversing over and over
                    setrecursionlimit(2)
                    self.run(direction = reverse, timeout = 3)
                except RuntimeError:
                    # FIXME Error here
                    debug("door.py run() Door stuck", level = 0)
                    # FIXME Test the finally here. Will it execute?
                    return False
                finally:
                    setrecursionlimit(default_recursion_limit)
            
            sleep(check_interval)
    
    
    def stop(self):
        '''Stops all motors'''
        debug("door.py stop() Stopping.", level = 0)
        debug("Before stopping:", level = 1)
        debug("motor.value: '" + str(motor.value) + "'", level = 1)
        motor.stop()
        debug("After stopping:", level = 1)
        debug("motor.value: '" + str(motor.value) + "'", level = 1)
    
    
    @property
    def current(self):
        '''Gets our motor current'''
        # FIXME Implement using an ADC
        return 1
        
        # Read the value of the current on the motor current sense ADC
        return ADC().channel(pin = current_pin, attn = ADC.ATTN_11DB).value()