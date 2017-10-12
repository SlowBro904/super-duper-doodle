#!/usr/bin/env python3.5
import test_suite
import lib.debugging
from lib.door_reed_switches import status

good = test_suite.good
debug = lib.debugging.printmsg

# Put a magnet on the dn reed switch
check = 'status()'
debug("status(): " + repr(status()))
# FIXME Why is it dn?
assert status() == 'dn', check
good(check)