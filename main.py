#!/usr/bin/env python3.5
# FIXME For production disable SSH
from lib.leds import leds
from lib.err import ErrCls
from lib.cloud import cloud
from lib.config import config
from lib.time import time, sleep
from lib.system import SystemCls
# TODO ScheduleCls for consistency
from lib.schedule import Schedule
from lib.update_sys import get_sys_updates
from lib.update_data import get_data_updates

leds.LED('good', default = True)

errors = ErrCls()
system = System()
schedule = ScheduleCls(system.attached_devices)

sched_buff = config.conf['SCHEDULE_BUFFER']
last_run = time()
while True:
    now = time()
    if now > (last_run + sched_buff):
        last_run = time()
        try:
            get_sys_updates()
            # FIXME Make sure we reboot after installing updates, I think we do
            # FIXME Receive this on the server
            cloud.send('version', system.version)
            # FIXME Also send the attached device status
            # FIXME Receive this on the server
            cloud.send('attached_devices', system.attached_devices)
            # FIXME Receive this on the server
            cloud.send('ntp_status', rtc.ntp_status)
            # TODO See about combining data and data
            get_data_updates()
            if cloud.send('errors.log', errors.log) == 'ack':
                errors.log = list()
        except RuntimeError:
            # Ignore if not connected
            pass
        
        schedule.run()
    # FIXME Do I have a race condition where I have an event inside this sleep?
    sleep(1)