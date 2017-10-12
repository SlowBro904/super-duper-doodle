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
        # self.events = {device: [(event_secs, 'cmd', 'args'),
        #                         (event_secs, 'cmd', 'args')],
        #                device: [(event_secs, 'cmd', 'args'),
        #                         (event_secs, 'cmd', 'args')]}
        self.events = dict()
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
                pass
            
            debug("temp_sched: '" + str(temp_sched) + "'", level = 1)
            
            for schedule, command in temp_sched.items():
                # Keys are stored comma-delimited in the JSON. Split out.
                # And convert to int() in the process.
                schedule = tuple(int(x) for x in schedule.split(','))
                
                if device not in self.schedules:
                    self.schedules[device] = dict()
                
                self.schedules[device][schedule] = command
            debug("self.schedules[device]: '" +
                    str(self.schedules[device]) + "'", level = 1)
            self.events[device] = self.get_todays_events(device)
            debug("self.events: '" + str(self.events) + "'", level = 1)
    
    
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
        
        today = now.day
        
        events = list()
        
        for event_time in self.schedules[device]:
            event_weekday, event_hour, event_min = event_time
            
            if event_weekday is not today:
                debug("event_weekday is not today", level = 1)
                continue
            
            event_secs = today_secs + (event_hour*60*60) + (event_min*60)
            
            if event_secs < now_secs:
                debug("event_secs (" + str(event_secs) +
                        ") < now_secs (" + str(now_secs) + ")", level = 1)
                # Skip events in the past
                # FIXME Do I want to?
                continue
            
            cmd, args = self.schedules[device][event_time]
            
            # FIXME How do I ensure they are sorted by time?
            events.append((event_secs, cmd, args))
        
        return events
    
    
    @property
    def next_event_time(self):
        '''Look across all schedules for all devices and return the time for
        the next scheduled event for any device'''        
        
        if self._next_event_time:
            return self._next_event_time
        
        for device in self.schedules:
            # Pull off the next scheduled event for this device
            this_event = self.events[device][0][0]
            
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
        # Get all items scheduled
        all_event_times = [x[0] for x in self.events[device]]
        debug("all_event_times: '" + str(all_event_times) + "'", level = 1)
        
        # Add a buffer to avoid a race condition if there is an event that
        # occurs between now and when the system goes to sleep.
        # This addresses a different situation than the 'while True:' in run().
        # FIXME Change all config items back to sane defaults. Right now this
        # is 86400.
        stop_time = int(time()) + config.conf['SCHEDULE_BUFFER']
        debug("stop_time: '" + str(stop_time) + "'", level = 1)
        
        # Get only the most recently scheduled items for this device
        due_times = [x for x in all_event_times if x <= stop_time]
        return [x for x in self.events[device] if x[0] in due_times]
    
    
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
            for device in self.events:
                due = self.get_due(device)
                
                if not due:
                    # No schedules, move on to the next device
                    continue
                
                # At least one item was scheduled
                items_scheduled = True
                
                # Get our command and arguments
                for event_time in due:
                    
                    event = self.schedules[device][event_time]
                    cmd, args = event[1:]
                    device_routine = DeviceRoutine(device)
                    
                    status = device_routine.run(cmd, args)
                    
                    # FIXME Do retries in cloud or mqtt if I don't already
                    cloud.send(device + '_status', status)
                    
                    # Remove what we just executed
                    self.events[device].remove(event)
            
            # Logic to know when to stop executing the outer while loop. If
            # this never gets set in this for loop we know we have no items
            # scheduled under any device, and so we can exit the while loop
            # as well.
            if not items_scheduled:
                break