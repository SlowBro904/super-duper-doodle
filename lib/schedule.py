import lib.debugging
from os import remove
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
        # Definitions in this class:
        # * Schedule: The weekday schedule of events. For example: (0,7,15) is
        #   on Monday, perform some operation at 7:15am.
        # * Event: The actual event on the calendar. For example, 1508155560 is
        #   Monday, October 16, 2017 8:06:00 AM GMT-04:00 DST.
        #
        # Data is communicated from the server in schedule format, and gets
        # converted to usable events in this class.
        #
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
        debug("schedule.py __init__() -------start-------", level = 1)
        self.status = dict()
        self.schedules = dict()
        self.todays_events = dict()
        self._next_event_time = None
        self.todays_executions_file = '/SmartBird/data/todays_executions.json'
        
        # FIXME Need a state.py module as well that records the expected state
        # and takes action if the device is not as expected.
        
        # FIXME If we have something in the file it does not check whether 
        # there is something new scheduled. So I ran it, it removed from todays
        # events, I cancelled it, I then updated the schedule server-side and
        # ran it again, it won't run, says door is [].
        today = datetime.now().weekday()
        try:
            with open(self.todays_executions_file) as f:
                self.todays_executions = loads(f.read())
            
            # Check that it's not zero length
            len(self.todays_executions)
            
            if ('day' in self.todays_executions and 
                self.todays_executions['day'] is not today):
                debug("schedule.py __init__() todays_executions_file " + 
                    "was from yesterday, will destroy that and create a new " +
                    "variable.", level = 1)
                remove(self.todays_executions_file)
                self.todays_executions = {'day': today}
        except (OSError, TypeError):
            # FIXME What about events close to midnight that are between today
            # and tomorrow, is there a concern scheduling by the day?
            debug("schedule.py __init__() todays_executions_file not found, " +
                "will create a new variable.", level = 1)
            self.todays_executions = {'day': today}
        
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
                level = 1)
            
            for schedule, command in temp_sched.items():
                # Keys are stored comma-delimited in the JSON. Split out.
                # And convert to int() in the process.
                schedule = tuple(int(x) for x in schedule.split(','))
                debug("schedule.py __init__() schedule: " + repr(schedule), 
                    level = 1)
                
                if device not in self.schedules:
                    self.schedules[device] = dict()
                
                self.schedules[device][schedule] = command
            
            try:
                debug("schedule.py __init__() self.schedules[device]: " +
                        repr(self.schedules[device]), level = 1)
            except KeyError:
                debug("schedule.py __init__() No data file or no schedule", 
                    level = 1)
                pass
            
            self.todays_events[device] = self.get_todays_events(device)
            debug("schedule.py __init__() self.todays_events: " + 
                repr(self.todays_events), level = 1)
            
            try:
                self.todays_executions[device]
            except KeyError:
                debug("schedule.py __init__() Since device not in " +
                    "self.todays_executions will create a new list.", 
                    level = 1)
                self.todays_executions[device] = list()
        
        debug("schedule.py __init__() self.todays_executions: " + 
            repr(self.todays_executions))
        debug("schedule.py __init__() -------end-------", level = 1)
    
    
    # TODO Should this be a @property instead?
    def get_todays_events(self, device):
        '''Gives us the events scheduled for today in the future.
        
        Ignores events from earlier today. Returns a list of tuples sorted by
        event time. Each tuple contains the event time (in seconds since
        epoch), command, and arguments.
        '''
        now = datetime.now()
        today = now.weekday()
        
        now_secs = now.second
        
        todays_events = list()
        
        for event_time in self.schedules[device]:
            event_weekday = event_time[0]
            
            if event_weekday is not today:
                debug("schedule.py get_todays_events() event_time (" +
                    repr(event_time) + ")" +
                    " event_weekday (" + repr(event_weekday) + 
                    ") is not today (" + repr(today) + ")", level = 1)
                continue
            debug("schedule.py get_todays_events() event_time (" +
                repr(event_time) + ")" +
                " event_weekday (" + repr(event_weekday) + 
                ") is for today (" + repr(today) + ")", level = 1)
            
            event_secs = self.tuple_to_secs(event_time)
            
            cmd, args = self.schedules[device][event_time]
            
            # FIXME How do I ensure they are sorted by time?
            todays_events.append([event_secs, cmd, args])
        
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
        '''Returns a list of all event times that are due now for a device'''
        # TODO This may become a problem when two events on two
        # different devices are scheduled at the same time. Doesn't
        # prevent go-live because I currently only have one device.
        # But must be fixed before adding the first item. Change
        # this TODO into a FIXME before adding the second device.
        
        # Get all schedules for all devices
        all_event_times = [x[0] for x in self.todays_events[device]]
        debug("schedule.py get_due() all_event_times: " + 
            repr(all_event_times), level = 1)
        
        # Add a buffer to avoid a race condition if there is an event that
        # occurs between now and when the system goes to sleep.
        # This addresses a different situation than the 'while True:' in run().
        # FIXME Change this and all config items back to sane defaults
        stop_time = int(time()) + config.conf['SCHEDULE_BUFFER']
        
        debug("schedule.py get_due() int(time()): " + repr(int(time())), 
            level = 1)
        debug("schedule.py get_due() config.conf['SCHEDULE_BUFFER']: " + 
            repr(config.conf['SCHEDULE_BUFFER']), level = 1)
        
        debug("schedule.py get_due() stop_time: " + repr(stop_time), level = 1)
        
        # Get times for all devices that are between now and stop_time
        all_due = [x for x in all_event_times if x <= stop_time]
        debug("schedule.py get_due() all_due: " + repr(all_due), level = 1)
        
        # Now for all due times for all devices for this device,
        device_due = [x[0] for x in self.todays_events[device] if x[0] in all_due]
        debug("schedule.py get_due() device_due: " + repr(device_due),
            level = 1)
        
        return device_due
    
    
    def tuple_to_secs(self, event_time):
        '''Takes an event time which is int(weekday), int(hour), int(minute)
        and converts it to an epoch time in seconds.
        '''
        now = datetime.now()
        
        now_hour, now_min, now_secs = now.hour, now.minute, now.second
        
        # Number of seconds since epoch as of 00:00 this morning
        today_secs = int(time()) - (now_hour*60*60) - (now_min*60) - now_secs
        
        event_weekday, event_hour, event_min = event_time
        
        return today_secs + (event_hour*60*60) + (event_min*60)
    
    
    def run(self):
        '''Run any events that are due now'''
        debug("schedule.py run() -----start-----", level = 1)
        # TODO I might want a per-device retry but quite difficult to implement
        # so let's wait 'til we need it
        device_retries = config.conf['DEVICE_RETRIES']
        
        # TODO Add some kind of expected time buffer on the server so we're
        # not continuously running events and killing our battery. Want a long
        # buffer between events, how about SCHEDULE_BUFFER x 5?
        
        # Keep re-checking the schedule until we're all clear. What might 
        # happen is we finish an event and the schedule starts for the next 
        # event. We want to keep checking until there are no more items
        # scheduled.
        while True:
            debug("schedule.py run() -----while True-----", 
                level = 1)
            debug("schedule.py run() self.todays_events: " + 
                repr(self.todays_events), level = 1)
            
            # We have not yet determined if any events have been scheduled
            # under any device.
            items_scheduled = False
            
            # TODO Run devices in parallel
            for device in self.todays_events:
                debug("schedule.py run() " +
                    "-----for device in self.todays_events-----", 
                    level = 1)
                
                # Logic to know when to stop executing the for loop device in 
                # self.todays_events. If this is empty we are done with events
                # that are due right now.
                debug("schedule.py run() len(self.todays_events[device]): " + 
                    repr(len(self.todays_events[device])), level = 1)
                
                if len(self.todays_events[device]) == 0:
                    debug("len(self.todays_events[device]) == 0 so we are " +
                        "done executing on due items for this device.", 
                        level = 1)
                    items_scheduled = False
                    break
                
                due = self.get_due(device)
                debug("schedule.py run() due: " + repr(due), level = 1)
                
                if not due:
                    debug("schedule.py run() No schedules due for " + 
                        str(device) + ", going to the next device", level = 1)
                    continue
                
                device_routine = DeviceRoutine(device)
                
                # Get our command and arguments
                for event_secs in due:
                    debug("schedule.py run() -----for event_secs in due-----", 
                        level = 1)
                    debug("schedule.py run() event_secs: " + repr(event_secs), 
                        level = 1)
                    debug("schedule.py run() self.schedules[device]: " + 
                        repr(self.schedules[device]), level = 1)
                    
                    # Convert each key in the self.schedules dict into seconds
                    # since epoch
                    schedules = {self.tuple_to_secs(k): v for k, 
                        v in self.schedules[device].items()}
                    debug("schedule.py run() schedules: " + repr(schedules), 
                        level = 1)
                    
                    event = schedules[event_secs]
                    debug("schedule.py run() event: " + repr(event), level = 1)
                    
                    cmd, args = event
                    debug("schedule.py run() cmd: " + repr(cmd), level = 1)
                    debug("schedule.py run() args: " + repr(args), level = 1)
                    
                    debug("schedule.py run() self.todays_executions: " +
                        repr(self.todays_executions), level = 1)
                    debug("schedule.py run() " +
                        "type(self.todays_executions[device]): " +
                        repr(type(self.todays_executions[device])), level = 1)
                    
                    if [event_secs,cmd,args] in self.todays_executions[device]:
                        debug("schedule.py run() This event (" + 
                            repr((event_secs, cmd, args)) + ") has already " +
                            "executed today. Skipping this execution.",
                            level = 1)
                        # Next event_secs
                        continue
                    debug("schedule.py run() This event (" + 
                        repr([event_secs, cmd, args]) + ") has not yet " +
                        "executed today. Executing now.", level = 1)
                    
                    # At least one item was scheduled
                    items_scheduled = True
                    
                    # FIXME Can I measure where current > 0? To ensure the
                    # motors are even running at all.
                    status = device_routine.run(cmd, args)
                    debug("schedule.py run() status: " + repr(status),
                        level = 1)
                    
                    # FIXME Listen for this on the cloud
                    # FIXME Review my QoS levels. Is 1 a problem?
                    cloud.send(device + '_status', status)
                    
                    # Note what we just executed
                    try:
                        self.todays_executions[device].append([event_secs, cmd, 
                            args])
                    except KeyError:
                        self.todays_executions[device] = [[event_secs, cmd, 
                            args]]
                    debug("schedule.py run() self.todays_executions: " +
                        repr(self.todays_executions), level = 1)
            
            # Logic to know when to stop executing the outer while loop. If
            # this never gets set in the for loops we know we have no items
            # scheduled under any device, and so we can exit the while loop
            # as well.
            if not items_scheduled:
                debug("schedule.py run() items_scheduled is False", level = 1)
                break
            debug("schedule.py run() items_scheduled is True", level = 1)
        
        if items_scheduled:
            debug("schedule.py run() At least one item was scheduled.")
            with open(self.todays_executions_file, 'w') as f:
                f.write(dumps(self.todays_executions))
            debug("Wrote to self.todays_executions_file.", level = 1)