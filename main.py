#!/usr/bin/env python3.5
# FIXME For production disable SSH
from lib.rtc import RTC
from lib.leds import leds
from lib.err import ErrCls
from lib.time import sleep
from lib.cloud import cloud
from lib.config import config
from lib.system import SystemCls
from lib.schedule import Schedule
from lib.datastore import DataStore
from lib.update_sys import get_sys_updates
from lib.update_data import get_data_updates

leds.LED('good', default = True)

rtc = RTC()
err = ErrCls()
system = System()
schedule = ScheduleCls(system.attached_devices)

try:
    get_sys_updates()
    # FIXME Receive this on the server
    cloud.send('version', system.version)
    # FIXME Also send the attached device status
    # FIXME Receive this on the server
    cloud.send('attached_devices', system.attached_devices)
    # FIXME Receive this on the server
    cloud.send('ntp_status', rtc.ntp_status)
    # TODO See about combining data and data
    get_data_updates()
except RuntimeError:
    # Ignore if not connected
    pass

sched_buff = config.conf['SCHEDULE_BUFFER']
last_run = rtc.now_secs()
while True:
    now = rtc.now_secs()
    if now > (last_run + sched_buff):
        last_run = rtc.now_secs()
        schedule.run()
        # FIXME If we have a connection error don't erase the log
        cloud.send('err.log', err.log)
        err.log = list()
    sleep(1)