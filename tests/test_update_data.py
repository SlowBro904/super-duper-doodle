#!/usr/bin/env python3.5
import test_suite
from json import loads
from lib.cloud import cloud
from os import listdir, remove
from lib.update_data import get_data_updates

good = test_suite.good

test_data = '/SmartBird/data/testing1.json'
try:
    remove(test_data)
except:
    pass

get_data_updates(get_all = True)
files = listdir('/SmartBird/data')

check = "get_data_updates() all"
assert 'testing1.json' in files, check
good(check)

with open(test_data) as f:
    contents = loads(f.read())

check = "get_data_updates() all contents"
assert contents['testing1'] == '123', check
good(check)

test_data = '/SmartBird/data/testing2.json'
try:
    remove(test_data)
except:
    pass

get_data_updates(get_all = False)
files = listdir('/SmartBird/data')

check = "get_data_updates() updates"
assert 'testing2.json' in files, check
good(check)

with open(test_data) as f:
    contents = loads(f.read())

check = "get_data_updates() updates contents"
assert contents['testing2'] == '456', check
good(check)