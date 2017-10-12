#!/usr/bin/env python3.5
import test_suite
import lib.debugging
from lib.cloud import cloud

good = test_suite.good
debug = lib.debugging.printmsg

debug("cloud.isconnected(): " + repr(cloud.isconnected()))

check = "cloud.isconnected()"
assert cloud.isconnected() == True, check
good(check)