#!/usr/bin/env python3.5
import test_suite
import lib.debugging
from lib.cloud import cloud
from os import listdir, remove
from lib.update_sys import get_sys_updates, _clean_failed_sys_updates

good = test_suite.good
debug = lib.debugging.printmsg

# FIXME Why am I not using temp_file for installing updates?
# FIXME Create some kind of one-off script run that I can have the customer
# reboot, download the script, execute, upload results
# TODO If we are not connected to the cloud umqtt/simple.py gives the following
# unhelpful error:
# File "umqtt/simple.py", line 176, in publish
# AttributeError: 'NoneType' object has no attribute 'write'

# Clean before starting
newly_created_dirs = ['testing.dir']

for file in newly_created_dirs:
    # FIXME Recursion for subdirs
    try:
        remove('/SmartBird/' + file)
    except: # TODO except what?
        pass

updated_files = ['testing.file', 'data/file_list.json']

for file in updated_files:
    try:
        remove('/SmartBird/' + file)
    except: # TODO except what?
        pass

debug("get_sys_updates()", level = 1)
get_sys_updates()
files = listdir('/SmartBird')

check = "Update directories"
assert 'testing.dir' in files, check
good(check)

check = "Update files"
assert 'testing.file' in files, check
good(check)

_clean_failed_sys_updates(newly_created_dirs, updated_files)
files = listdir('/SmartBird')

# FIXME Mess up a file then run the clean

check = "_clean_failed_sys_updates()"
assert 'testing.dir' not in files, check
good(check)