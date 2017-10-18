#!/usr/bin/env python3.5
# TODO I haven't fully tested at least run() and maybe others
import test_suite
import lib.debugging
from time import time
from json import dumps
from datetime import datetime
from lib.config import config
from lib.schedule import Schedule

good = test_suite.good
debug = lib.debugging.printmsg

now = datetime.now()
now_hour, now_min, now_secs = now.hour, now.minute, now.second
# Number of seconds since epoch as of 00:00 this morning
today_secs = int(time()) - (now_hour*60*60) - (now_min*60) - now_secs

# FIXME This didn't fail on now.day, which returned day of the month
today = now.weekday()

# Turn our schedule into a comma-delimited string
temp_sched1 = ','.join([str(today), str(23), str(56)])
temp_sched2 = ','.join([str(today), str(23), str(57)])
temp_sched3 = ','.join([str(today), str(23), str(58)])
temp_sched4 = ','.join([str(today), str(23), str(59)])
# FIXME Create a command to run, and a parameter for it
test_schedule1 = {  temp_sched1: ['test1_cmd', 'test1_arg'],
                    temp_sched2: ['test2_cmd', 'test2_arg']}
test_schedule2 = {  temp_sched3: ['test3_cmd', 'test3_arg'],
                    temp_sched4: ['test4_cmd', 'test4_arg']}
with open('/SmartBird/data/test1.json', 'w') as f:
    f.write(dumps(test_schedule1))
with open('/SmartBird/data/test2.json', 'w') as f:
    f.write(dumps(test_schedule2))

schedule = Schedule(['test1','test2'])

debug("schedule.get_due('test1'): '" +
        str(schedule.get_due('test1')) + "'", level = 1)
debug("schedule.get_due('test1')[0][0]: '" +
        str(schedule.get_due('test1')[0][0]) + "'", level = 1)
debug("schedule.get_due('test1')[0][1:]: '" +
        str(schedule.get_due('test1')[0][1:]) + "'", level = 1)
debug("today_secs: '" + str(today_secs) + "'", level = 1)
debug("config.conf['SCHEDULE_BUFFER']: '" +
        str(config.conf['SCHEDULE_BUFFER']) + "'", level = 1)
due = schedule.get_due('test1')

check = 'get_due()[0][0]'
assert due[0][0] <= today_secs + int(config.conf['SCHEDULE_BUFFER']), check
good(check)

check = 'get_due()[0][1:]'
assert due[0][1:] == ('test1_cmd','test1_arg'), check
good(check)

check = 'get_todays_events()'
events = schedule.get_todays_events('test1')
event_secs = today_secs + (23*60*60) + (56*60)
debug("events: " + str(events) + "'", level = 1)
debug("event_secs: " + repr(event_secs), level = 1)
assert events[0] == (event_secs, 'test1_cmd', 'test1_arg'), check
good(check)

check = 'next_event_time()'
debug("schedule.next_event_time(): '" +
        str(schedule.next_event_time) + "'", level = 1)
assert schedule.next_event_time == event_secs, check
good(check)