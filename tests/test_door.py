#!/usr/bin/env python3.5
import test_suite
import lib.debugging
from time import sleep
import lib.device_routines
from lib.config import config
from gpiozero import OutputDevice

good = test_suite.good
debug = lib.debugging.printmsg
door = lib.device_routines.DeviceRoutine('door')

# FIXME How do I test this?
#check = 'MotorCls().current'
#assert MotorCls().current is not 0, check
#good(check)

check = "door('operate', 'up')"
door.run('operate', 'up')
debug("door.module.motor.value: " + repr(door.module.motor.value))
assert door.module.motor.value == 1.0, check
good(check)

sleep(1)

check = "motor.operate('stop')"
door.run('operate', 'stop')
debug("door.module.motor.value: " + repr(door.module.motor.value))
assert door.module.motor.value == 0.0, check
good(check)