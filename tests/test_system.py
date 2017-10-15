#!/usr/bin/env python3.5
import test_suite
import lib.debugging
from json import loads
from lib.cmd import cmd
from lib.system import SystemCls

system = SystemCls()

good = test_suite.good
debug = lib.debugging.printmsg

with open('/SmartBird/config/version.json') as f:
    version = loads(f.read())

check = "system.version correct"
assert system.version == version, check
good(check)

check = "system.attached_devices"
assert len(system.attached_devices) >= 1, check
good(check)

check = "door in devices"
assert 'door' in system.attached_devices, check
good(check)

debug("cmd('lib/get_serial.sh'): " + repr(cmd('lib/get_serial.sh')))
debug("system.serial: " + repr(system.serial))

check = "serial"
assert cmd('lib/get_serial.sh')[0] == system.serial, check
good(check)