from lib.cmd import cmd
from os import remove, rename
import lib.debugging as debugging

debug = debugging.printmsg

def create(target):
    '''Creates a temp file in the format of /tmp/target.tmp and returns a
    file name
    '''    
    # Ignore any preceding path, we're going to create our file in /tmp.
    target_basename = target.split('/')[-1]
    temp_file_name = cmd('mktemp /tmp/' + target_basename + 
        '.XXXXX.tmp')[0]
    
    debug("temp_file_name: '" + str(temp_file_name) + "'", level = 1)
    
    return temp_file_name


def install(temp_file, target):
    '''Takes a temp file and installs the temp file into the target, backing up
    any existing file. Must exist in /SmartBird/.
    '''
    # TODO Allow different device paths like /SmartCamera/ or something.
    with open(temp_file) as temp_fileH:
        if not target.startswith('/SmartBird/'):
            target = '/SmartBird/' + target
        
        try:
            # Delete any old backup file TODO Create
            # some way of restoring from backup
            self.remove(target + '.bak')
        except: # TODO Add precise exception reason
            pass # Ignore err if it does not exist.
        
        try:
            # Create a backup of the current file
            rename(target, target + '.bak')
        except OSError:
            # FIXME Error is exactly 'error renaming file'
            pass
        
        # Install the temp as the new file
        with open(target, 'w') as f:
            for row in temp_fileH.readlines():
                f.write(row)
        
    remove(temp_file)
    return True