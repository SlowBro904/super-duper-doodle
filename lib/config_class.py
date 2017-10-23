import lib.temp_file
from os import remove
from json import loads, dumps
import lib.debugging as debugging

debug = debugging.printmsg
testing = debugging.testing

class Config(object):
    def __init__(self, config_file, defaults_file):
        '''Provides a dictionary with keys and values coming from the config
        file's options and values.
        
        If the config file is unreadable or missing it will load values from 
        the defaults file.
        '''
        self.config_file = config_file
        self.defaults_file = defaults_file
        self.conf = self.load_config()
    
    
    def load_config(self):
        '''Loads the config file from flash into memory.
        
        If it doesn't exist it will copy the defaults file into place as the 
        new config file and load from that.
        '''
        try:
            open(self.config_file)
            debug("Successfully opened our config file", level = 1)
        except OSError:
            debug("Resetting to defaults", level = 1)
            # TODO What if even this fails
            self.reset_to_defaults()
        
        
        with open(self.config_file) as f:
            debug("Reading our config file...", level = 1)
            if debugging.default_level > 0:
                debug("type(f): '" + str(type(f)) + "'", level = 1)
                debug("f: '" + str(f) + "'", level = 1)
                debug("f.read(): '" + str(f.read()) + "'", level = 1)
                f.seek(0)
                debug("Contents: " + str(loads(f.read())), level = 1)
                f.seek(0)
            
            #try:
            return loads(f.read())
            #except ValueError:
            #    # FIXME What? Means we have a corrupt config. I think reset to
            #    # default and error.
            #    pass
    
    
    def reset_to_defaults(self):
        '''Resets the config file to defaults'''
        with open(self.defaults_file) as f:
            debug("Loading defaults into memory", level = 1)
            defaults = loads(f.read())
        
        
        try:
            debug("Removing existing config", level = 1)
            remove(self.config_file)
        except OSError: # FIXME Get the precise exception
            # Ignore if it does not exist
            pass
        
        
        with open(self.config_file, 'w') as f:
            debug("Writing a new config file from defaults", level = 1)
            # Write the new config file from the defaults
            f.write(dumps(defaults))
        
        debug("Loading the new config file to memory", level = 1)
        self.conf = self.load_config()
    
    
    # TODO I thought I could make this into a setter but was not successful
    def update(self, updates):
        '''Takes a dict of updates and updates the config file with the new
        parameters and values, and also updates the values in memory
        '''
        debug("Attempting to update our config file", level = 1)
        
        if not isinstance(updates, dict):
            debug("Did not pass a dict()", level = 1)
            debug("config_class.py update() updates: " + repr(updates),
                level = 1)
            return False
        
        found = False
        for parameter in updates.keys():
            if parameter not in self.conf:
                # Next parameter
                debug("Attempted to update the config file with", level = 1)
                debug("a nonexistant parameter " + repr(parameter), level = 1)
                continue
        
            # TODO There's an anti-pattern for this...    
            found = True
        
        if not found:
            debug("No existing config parameters found in update", level = 1)
            return False
        
        for parameter, value in updates.items():
            self.conf[parameter] = value
        
        
        # Update the config file
        #try:
        with open(self.config_file, 'w') as f:
            debug("Updating our config file on flash", level = 1)
            # FIXME Also backup the config file and/or get temp file working,
            # I don't want some error leaving us without a config
            f.write(dumps(self.conf))
            #except:
            #    warning = ("Cannot update config file",
            #                "('config_class.py','update')")
            #    self.err.warning(warning)
        
            # FIXME Use temp files
            # Install the temp file
            #temp_file.install(f, self.config_file)
            #    warning = ("Cannot update config file",
            #                "('config_class.py','update')")
            #    self.err.warning(warning)
            # TODO Delete the temp file
        
        # Update the values in memory from flash
        self.conf = self.load_config()
        debug("New config: " + str(self.conf), level = 1)