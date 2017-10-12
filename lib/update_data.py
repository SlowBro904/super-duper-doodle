import lib.debugging
import lib.temp_file
from lib.err import ErrCls
from lib.cloud import cloud
from json import dumps, loads
from os import listdir, remove, mkdir

errors = ErrCls()
debug = lib.debugging.printmsg

def get_data_updates(get_all = False):
    '''Get recent data updates such as new door schedules from our 
    cloud servers.
    
    We can optionally specify which updates to get, whether only the latest
    or all data files if for example we just did a factory reset.
    
    This can also be specified by writing True in JSON format into
    /SmartBird/get_all_data_files.json which will get deleted once read.
    '''
    # TODO If our schedule is incomplete for some reason error/warn
    if 'data' not in listdir('/SmartBird'):
        mkdir('data')
    
    get_all_flag = '/SmartBird/get_all_data_files.json'
    
    try:
        with open(get_all_flag) as f:
            get_all = loads(f.read())
        
        remove(get_all_flag)
    except OSError:
        # Does not exist, ignore
        pass
    
    #try:
    if get_all:
        updates = cloud.send('get_data_updates', 'all')
    else:
        updates = cloud.send('get_data_updates', 'latest')
    #except RuntimeError as warning:
    #    errors.warning(warning + " ('updates.py', 'get_data_updates')")
    #    return False
    
    if not updates:
        return True
    
    data = dict()
    for data_file, update in updates.items():
        debug("update_data.py get_data_updates() update: '" +
                str(update) + "'", level = 1)
        
        parameter, value = update
        
        myfile = '/SmartBird/data/' + data_file
        try:
            # Read the original file
            with open(myfile) as f:
                data[data_file] = loads(f.read())
        except OSError:
            # File doesn't exist yet. We'll create it in memory first.
            data[data_file] = dict()
        
        data[data_file][parameter] = value
    
    
    debug("update_data.py get_data_updates() data: " + repr(data), level = 1)
    
    for data_file in data:
        # TODO Do general Pythonic cleanup and refactor everywhere
        #try:
        debug("update_data.py lib.temp_file.create(data_file): '" +
                str(lib.temp_file.create(data_file)) + "'", level = 1)
        my_temp = lib.temp_file.create(data_file)
        debug("update_data.py get_data_updates() my_temp: '" + 
                str(my_temp) + "'", level = 1)
        success = False
        with open(my_temp, 'w') as f:
            if f.write(dumps(data[data_file])):
                debug("update_data.py get_data_updates() " +
                        "f.write(dumps(data[data_file])) success", level = 1)
                debug("update_data.py get_data_updates() " +
                        "listdir('/tmp')" +
                        str(listdir('/tmp')) + "'", level = 1)
                success = True
        
        if not success:
            # FIXME Some error somewhere
            remove(my_temp)
        else:
            # TODO Maybe make this an exception
            if lib.temp_file.install(my_temp, 
                '/SmartBird/data/' + data_file):
                cloud.send('got_data_update', data_file)
                #debug("update_data.py get_data_updates() " +
                #        "listdir('/SmartBird/data')" +
                #        str(listdir('/SmartBird/data')) + "'")
        #except OSError:
        #    warning = ("Failed to get data updates.",
        #                " ('updates.py', 'get_data_updates')")
        #    errors.warning(warning)