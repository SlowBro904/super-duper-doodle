import lib.debugging
from lib.leds import leds
from lib.err import ErrCls
from hashlib import sha512
from lib.cloud import cloud
from re import sub as re_sub
from binascii import hexlify
from lib.reboot import reboot
from lib.config import config
from json import loads, dumps
from lib.system import SystemCls
from os import remove, rename, mkdir, rmdir, listdir

errors = ErrCls()
system = SystemCls()
debug = lib.debugging.printmsg
testing = lib.debugging.testing

file_list = '/SmartBird/data/file_list.json'
updated_files_list = '/SmartBird/data/updated_files.json'

def _clean_failed_sys_updates(newly_created_dirs, updated_files):
    '''Cleans up failed system updates. All or nothing.'''
    debug("update_sys.py _clean_failed_sys_updates() newly_created_dirs: " +
            repr(newly_created_dirs), level = 1)
    debug("update_sys.py _clean_failed_sys_updates() updated_files: " +
            repr(updated_files), level = 1)
    
    # FIXME Test this
    # Even though we are in the _clean_failed_sys_updates() function, this
    # would only be called from the get_sys_updates() function.
    warning = ("Update failure. Reverting.",
                "('update_sys.py', 'get_sys_updates')")
    errors.warn(warning)
    
    # FIXME Did I test this? Can't just go erasing things. Test partial update.
    for new_file in updated_files:
        try:
            remove(new_file)
            debug("Removed file: " + repr(new_file), level = 1)
        except OSError:
            # Ignore if not able to
            debug("Cannot remove file: " + repr(new_file), level = 1)
            pass
    
    for new_dir in newly_created_dirs:
        debug("Attempting to remove dir: " + repr(new_dir), level = 1)
        # FIXME Add recursion, sort by dir listing so I always start w/ topmost
        if len(listdir(new_dir)) > 0:
            # Ignore non-empty directories
            debug("Dir not empty, not deleting: " + repr(new_dir), level = 1)
            continue
        
        try:
            rmdir(new_dir)
            debug("Removed dir: " + repr(new_dir), level = 1)
        except OSError:
            # Ignore if not able to
            debug("Cannot remove dir: " + repr(new_dir), level = 1)
            pass


def curr_client_ver():
    '''Get the current client version on the server and compare to our version.
    
    If we are current return True, else return False.
    '''
    # FIXME What about updating individual clients? What about one-off client
    # commands?
    # FIXME Wrap with except RuntimeError
    
    return system.version == cloud.send('curr_client_ver')


def new_dirs(server_dirs):
    '''Gets any directories we don't have which need to be created'''
    new_dirs = list()
    for dir in server_dirs:
        # FIXME On the server side do I recursively find both dirs and files?
        # FIXME If possible, record watchdog resets
        
        # Split apart the last directory
        try:
            dirname_dir, basename_dir = dir.rsplit('/', 1)
        except ValueError:
            # FIXME Actual error is
            # ValueError: not enough values to unpack (expected 2, got 1)
            dirname_dir = ''
            basename_dir = dir
        
        if not basename_dir in listdir('/SmartBird/' + dirname_dir):
            new_dirs.append(dir)
    
    return new_dirs


def new_files(server_files, check_sums = True):
    '''Checks the file list to see if anything needs to be updated/repaired'''
    new_files = list()
    for file, expected_sha in server_files.items():
        file = '/SmartBird/' + file
        try:
            open(file)
        except: # FIXME Except what
            new_files.append(file)
            # Don't need to check anything else, go to the next file
            continue
        
        if not check_sums:
            new_files.append(file)
        else:
            stored_sha = file_sha512(file)
            
            if stored_sha != expected_sha:
                new_files.append(file)
    
    return new_files


def file_sha512(file):
    stored_sha = sha512()
    with open(file, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            stored_sha.update(chunk)
    
    return hexlify(stored_sha.digest()).decode('utf-8')


def get_sys_updates():
    '''Update the scripts on our system'''
    # FIXME Is EVERY line of code tested?
    fetch_latest_list = False
    if not curr_client_ver():
        fetch_latest_list = True
    else:
        try:
            with open(file_list) as f:
                file_list_contents = loads(f.read())
        except OSError:
            # FIXME Also [Errno 2] ENOENT
            fetch_latest_list = True
    
    if fetch_latest_list:
        file_list_contents = cloud.send('get_file_list')
        with open(file_list, 'w') as f:
            f.write(dumps(file_list_contents))
    
    debug("file_list_contents: '" + str(file_list_contents) + "'", level = 1)
    debug("type(file_list_contents): '" +
            str(type(file_list_contents)) + "'", level = 1)
    debug("len(file_list_contents): '" +
            str(len(file_list_contents)) + "'", level = 1)
    
    newly_created_dirs = list()
    for new_dir in new_dirs(file_list_contents[1]):
        debug("Creating new_dir '" + str(new_dir) + "'", level = 1)
        
        # MicroPython lacks the ability to create the entire path chain with
        # one command. Build the chain creating one directory at a time
        tempdir = '/SmartBird'
        for subdir in new_dir.split('/'):    
            tempdir += '/' + subdir
            try:
                debug("Creating tempdir '" + str(tempdir) + "'", level = 1)
                mkdir(tempdir)
            except OSError:
                # FIXME Actual error is OSError: file exists:
                pass
        
        newly_created_dirs.append(new_dir)
    
    if not new_files(file_list_contents[2]):
        return None
    
    # FIXME Notify the web admin we are updating and don't allow the client to
    # do anything
    
    updated_files = list()
    
    debug("new_files(file_list_contents[2]): '" + 
            str(new_files(file_list_contents[2])) + "'", level = 1)
    
    for myfile in new_files(file_list_contents[2]):
        # Remove all but the filename
        get_file = myfile.rsplit('/', 1)[1]
        
        debug("update_sys.py get_sys_updates() file: '" + 
                str(get_file) + "'", level = 1)
        debug("update_sys.py get_sys_updates() " +
                "cloud.send('get_file', file): '" +
                str(cloud.send('get_file', get_file)) + "'", level = 1)
        
        contents, expected_sha = cloud.send('get_file', get_file)
        new_file = myfile + '.new'
        
        try:
            # Create the file as .new and upon reboot our system will see the
            # .new file and delete the existing version, install the new.
            with open(new_file, 'w') as f:
                for row in contents:
                    f.write(row)
                debug("Created " + repr(new_file), level = 1)
        except: # FIXME except what?
            debug("Couldn't write new_file '" + str(new_file) + "'", level = 1)
            _clean_failed_sys_updates(newly_created_dirs, updated_files)
            
            # Empty the list
            updated_files = list()
            break
        
        stored_sha = file_sha512(new_file)
        
        if stored_sha == expected_sha:
            updated_files.append(new_file)
        else:
            debug("stored_sha '" + str(stored_sha) + "' "
                    " != expected_sha '" + str(expected_sha) + "'", level = 1)
            _clean_failed_sys_updates(newly_created_dirs, updated_files)
            
            # Empty the list
            updated_files = list()
            break
    
    debug("Contents of the updated_files variable: " +
            repr(updated_files), level = 1)
    
    if updated_files:
        debug("The updated_files variable is not empty", level = 1)
        #try:
        with open(updated_files_list, 'w') as f:
            f.write(dumps(updated_files))
        debug("Was able to write the updated_files " +
                "variable to " + str(updated_files_list), level = 1)
        # FIXME Test and get this working
        #except Exception, e: # FIXME except what?
        #    debug("Not able to write the updated_files " +
        #            "variable to " + str(updated_files_list)) + 
        #            ", error was: " + str(e)
        #    _clean_failed_sys_updates(newly_created_dirs, updated_files)
        
        install_updates()


def install_updates():
    '''Install any recent updates. Typically runs at boot.'''
    # TODO Combine with get_sys_updates()
    # TODO Why don't I use temp_file to create new files then install those?
    # Would get weird if I have the same file name in two places. Maybe change
    # temp_file to create a file as something.XXXXX.tmp, and create an install
    # map for this function.
    # FIXME Test upgrading this file (updates.py) as well
    # TODO I'm not doing this at boot 'cause I'll bet we can update files w/out
    # first rebooting. Update on the fly then reboot then proceed.
    # I removed this from boot because LED() goes back to black on reboot.
    # Maybe one day retain that setting at boot but not now. Simpler.
    do_reboot = False
    do_upgrade = True
    
    try:
        open(updated_files_list)
    except OSError:
        debug("update_sys.py install_updates() Can't open " + 
            str(updated_files_list), level = 1)
        return

    # Ensure all new files exist
    with open(updated_files_list) as f:
        for new_file in loads(f.read()):
            try:
                open(new_file)
            except OSError:
                debug("update_sys.py install_updates() Can't open " + 
                    str(new_file), level = 1)
                do_upgrade = False
                break
    
    if do_upgrade:
        # Install any new versions of scripts
        with open(updated_files_list) as f:
            for new_file in loads(f.read()):
                # Set the flag to reboot after installing new files
                # TODO I think there is an anti-pattern for this...
                do_reboot = True
                
                # Remove .new suffix from the filename
                myfile = re_sub(r'.new$', '', new_file)
                
                try:
                    # TODO I get nervous deleting current in use system files.
                    # At least I do ensure the .new file really does exist. I 
                    # don't know a good clean way to back up the old files and 
                    # revert. Hmm. Button maybe. Perhaps when doing a factory
                    # reset, revert to factory versions of scripts.
                    remove(myfile)
                except OSError: # FIXME Get the exact exception type
                    # Ignore if it does not exist
                    pass
                
                rename(new_file, myfile)
    
    try:
        remove(updated_files_list)
    except OSError: # FIXME Get the exact exception type
        # Ignore if it does not exist
        pass
    
    # FIXME Uncomment
    #if do_reboot:
    #    if not testing:
    #        from reboot import reboot
    #        reboot()