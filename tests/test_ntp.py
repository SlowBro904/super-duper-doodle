#!/usr/bin/env python3.5
import test_suite

import lib.ntp
from datetime import datetime

good = test_suite.good

check = "lib.ntp.status()"
assert lib.ntp.status() == True, check
good(check)

check = "NTP working"
assert datetime.now().year >= 2017, check
good(check)