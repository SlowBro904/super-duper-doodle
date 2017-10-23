#!/usr/bin/env python3.5
# FIXME For production disable SSH
import lib.ntp
import lib.debugging
from lib.leds import leds
from lib.err import ErrCls
from lib.cloud import cloud
from time import time, sleep
from lib.config import config
from lib.system import SystemCls
# TODO ScheduleCls for consistency
from lib.schedule import Schedule
from lib.update_sys import get_sys_updates
from lib.update_data import get_data_updates

leds.LED('good', default = True)

errors = ErrCls()
system = SystemCls()
debug = lib.debugging.printmsg

def updates():
    try:
        debug("main.py get_sys_updates()", level = 1)
        get_sys_updates()
        # FIXME Receive this on the server
        debug("main.py cloud.send version", level = 1)
        cloud.send('version', system.version)
        # FIXME Also send the attached device status
        # FIXME Receive this on the server
        debug("main.py cloud.send attached_devices", level = 1)
        cloud.send('attached_devices', system.attached_devices)
        # FIXME Receive this on the server
        debug("main.py cloud.send lib.ntp.status()", level = 1)
        cloud.send('lib.ntp_status', lib.ntp.status())
        debug("main.py get_data_updates()", level = 1)
        get_data_updates()
        debug("main.py cloud.send errors.log", level = 1)
        if cloud.send('errors.log', errors.log) == 'ack':
            errors.log = list()
    except RuntimeError:
        # Ignore if not connected
        debug("main.py not connected", level = 1)
        pass

updates()

debug("main.py Schedule(system.attached_devices)", level = 1)

# Add 1 for the sleep at the end
# FIXME Set this value, and all values, to sensible defaults and live config
sched_buff = config.conf['SCHEDULE_BUFFER'] + 1

last_run = time()

while True:
    debug("main.py ---------------", level = 1)
    debug("main.py loop start", level = 1)
    now = time()
    debug("main.py last_run: " + repr(last_run), level = 1)
    debug("main.py now: " + repr(last_run), level = 1)
    debug("main.py sched_buff: " + repr(sched_buff), level = 1)
    debug("main.py last_run + sched_buff: " + repr(last_run + sched_buff), 
        level = 1)
    debug("main.py now > (last_run + sched_buff): " + 
        repr(now > (last_run + sched_buff)), level = 1)
    
    if now > (last_run + sched_buff):
        # FIXME Constantly running. May be because too short sched_buff.
        last_run = time()
        updates()
        
        debug("main.py schedule.run()", level = 1)
        schedule = Schedule(system.attached_devices)
        schedule.run()
    # FIXME Do I have a race condition where I have an event inside this sleep?
    # FIXME Do I want no sleep? More? Check CPU usage.
    sleep(5)
    debug("main.py loop start", level = 1)