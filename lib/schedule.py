import lib.debugging
from time import time
from lib.err import ErrCls
from lib.cloud import cloud
from lib.config import config
from json import dumps, loads
from datetime import datetime
from lib.device_routines import DeviceRoutine

debug = lib.debugging.printmsg
testing = lib.debugging.testing

errors = ErrCls()

class Schedule(object):
    def __init__(self, devices):
        '''Sets up scheduled events for our devices'''
        # The data structures in this class look like the following:
        # device.json = {'weekday,hour,min': ('cmd', 'args'),
        #                'weekday,hour,min': ('cmd', 'args')}
        # self.schedules = {device: {(weekday, hour, min): ('cmd', 'args'), 
        #                            (weekday, hour, min): ('cmd', 'args')}
        #                   device: {(weekday, hour, min): ('cmd', 'args'), 
        #                            (weekday, hour, min): ('cmd', 'args')}}
        # self.todays_events = {device: [(event_secs, 'cmd', 'args'),
        #                         (event_secs, 'cmd', 'args')],
        #                device: [(event_secs, 'cmd', 'args'),
        #                         (event_secs, 'cmd', 'args')]}
        debug("schedule.py __init__() start", level = 1)
        self.todays_events = dict()
        self.status = dict()
        self.schedules = dict()
        self._next_event_time = None
        
        for device in devices:
            try:
                device_file = '/SmartBird/data/' + device + '.json'
                with open(device_file) as f:
                    temp_sched = loads(f.read())
            # FIXME Should be OSError: [Errno 2] ENOENT
            except OSError:
                # Ignore errors. If we have zero schedules nothing will run.
                temp_sched = dict()
            
            debug("schedule.py __init__() temp_sched: " + repr(temp_sched),
                level = 0)
            
            for schedule, command in temp_sched.items():
                # Keys are stored comma-delimited in the JSON. Split out.
                # And convert to int() in the process.
                schedule = tuple(int(x) for x in schedule.split(','))
                debug("schedule.py __init__() schedule: " + repr(schedule))
                
                if device not in self.schedules:
                    self.schedules[device] = dict()
                
                self.schedules[device][schedule] = command

            try:
                debug("schedule.py __init__() self.schedules[device]: " +
                        repr(self.schedules[device]), level = 0)
                self.todays_events[device] = self.get_todays_events(device)
                debug("schedule.py __init__() self.todays_events: " + 
                    repr(self.todays_events), level = 0)
            except KeyError:
                debug("schedule.py __init__() No data file or no schedule", 
                    level = 0)
                pass
        debug("schedule.py __init__() end", level = 1)
    
    
    def get_todays_events(self, device):
        '''Gives us the events scheduled for today in the future.

        Ignores events from earlier today. Returns a list of tuples sorted by
        event time. Each tuple contains the event time (in seconds since
        epoch), command, and arguments.
        '''
        now = datetime.now()
        now_hour, now_min, now_secs = now.hour, now.minute, now.second
        # Number of seconds since epoch as of 00:00 this morning
        today_secs = int(time()) - (now_hour*60*60) - (now_min*60) - now_secs
        
        today = now.weekday()
        
        todays_events = list()
        
        for event_time in self.schedules[device]:
            event_weekday, event_hour, event_min = event_time
            
            if event_weekday is not today:
                debug("schedule.py get_todays_events() event_time (" +
                    repr(event_time) + ")" +
                    "event_weekday (" + repr(event_weekday) + 
                    ") is not today (" + repr(today) + ")", level = 0)
                continue
            
            event_secs = today_secs + (event_hour*60*60) + (event_min*60)
            
            if event_secs < now_secs:
                debug("schedule.py get_todays_events()event_secs (" + 
                        str(event_secs) + ") < now_secs (" + str(now_secs) + 
                        ") so skipping events in the past", level = 0)
                # Skip events in the past
                # FIXME Do I want to?
                continue
            
            cmd, args = self.schedules[device][event_time]
            
            # FIXME How do I ensure they are sorted by time?
            todays_events.append((event_secs, cmd, args))
        
        return todays_events
    
    
    @property
    def next_event_time(self):
        '''Look across all schedules for all devices and return the time for
        the next scheduled event for any device'''        
        
        if self._next_event_time:
            return self._next_event_time
        
        for device in self.schedules:
            # Pull off the next scheduled event for this device
            this_event = self.todays_events[device][0][0]
            
            if not self._next_event_time:
                self._next_event_time = this_event
                
                # Next device
                continue
            
            # If the event we're looking at is sooner than our next event
            if this_event < self._next_event_time:
                self._next_event_time = this_event
        
        return self._next_event_time
    
    
    def get_due(self, device):
        '''Returns a list of all events that are due now for a given device'''
        # Get all schedules for all devices
        all_event_times = [x[0] for x in self.todays_events[device]]
        debug("schedule.py get_due() all_event_times: " + 
            repr(all_event_times), level = 0)
        
        # Add a buffer to avoid a race condition if there is an event that
        # occurs between now and when the system goes to sleep.
        # This addresses a different situation than the 'while True:' in run().
        # FIXME Change this and all config items back to sane defaults
        stop_time = int(time()) + config.conf['SCHEDULE_BUFFER']
        
        debug("schedule.py get_due() int(time()): " + repr(int(time())), 
            level = 0)
        debug("schedule.py get_due() config.conf['SCHEDULE_BUFFER']: " + 
            repr(config.conf['SCHEDULE_BUFFER']), level = 0)
        
        debug("schedule.py get_due() stop_time: " + repr(stop_time), level = 0)
        
        # Get times for all devices that are between now and stop_time
        all_due = [x for x in all_event_times if x <= stop_time]
        debug("schedule.py get_due() all_due: " + repr(all_due), level = 0)
        
        # Now for all due times for all devices for this device,
        device_due = [x[0] for x in self.todays_events[device] if x[0] in all_due]
        debug("schedule.py get_due() device_due: " + repr(device_due),
            level = 0)
        
        return device_due
    
    
    def run(self):
        '''Run any events that are due now'''
        # TODO I might want a per-device retry but quite difficult to implement
        # so let's wait 'til we need it
        device_retries = config.conf['DEVICE_RETRIES']
        
        # FIXME Add some kind of expected time buffer on the server so we're
        # not continuously running events and killing our battery. Want a long
        # buffer between events, how about SCHEDULE_BUFFER x 5?
        
        # Keep re-checking the schedule until we're all clear. What might 
        # happen is we finish an event and the schedule starts for the next 
        # event. We want to keep checking until there are no more items
        # scheduled.
        items_scheduled = False
        while True:
            debug("schedule.py run() self.todays_events: " + 
                repr(self.todays_events), level = 0)
            
            for device in self.todays_events:
                debug("schedule.py run() starting loop on device " + 
                    repr(device), level = 0)
                
                due = self.get_due(device)
                debug("schedule.py run() due: " + repr(due))
                
                if not due:
                    debug("schedule.py run() No schedules, go to next device", 
                        level = 0)
                    continue
                
                # At least one item was scheduled
                items_scheduled = True
                
                # Get our command and arguments
                for event_time in due:
                    debug("schedule.py run() event_time: " + repr(event_time), 
                        level = 0)
                    debug("schedule.py run() self.schedules[device]: " + 
                        repr(self.schedules[device]), level = 0)
                    
                    # FIXME KeyError because event_time is in seconds but
                    # self.schedules[device] is (d, h, m). Maybe create 
                    # secs_to_tuple()
                    event = self.schedules[device][event_time]
                    debug("schedule.py run() event: " + repr(event), level = 0)
                    
                    cmd, args = event[1:]
                    debug("schedule.py run() cmd: " + repr(cmd), level = 0)
                    debug("schedule.py run() args: " + repr(args), level = 0)
                    
                    device_routine = DeviceRoutine(device)
                    
                    status = device_routine.run(cmd, args)
                    debug("schedule.py run() status: " + repr(status),
                        level = 1)
                    
                    # FIXME Do retries in cloud or mqtt if I don't already
                    cloud.send(device + '_status', status)
                    
                    # Remove what we just executed
                    # FIXME And save it to disk
                    self.todays_events[device].remove(event)
            
            # Logic to know when to stop executing the outer while loop. If
            # this never gets set in this for loop we know we have no items
            # scheduled under any device, and so we can exit the while loop
            # as well.
            if not items_scheduled:
                debug("schedule.py run() items_scheduled is False", level = 0)
                break