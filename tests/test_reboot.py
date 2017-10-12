#!/usr/bin/env python3.5
import test_suite
from lib.reboot import reboot

check = 'reboot()'
print("Should get '[DEBUG] Simulating reboot' on the next line.")
reboot()