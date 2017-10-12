#!/usr/bin/env python3.5
import test_suite
from os import remove
import lib.temp_file as temp_file
import lib.debugging as debugging

good = test_suite.good
debug = debugging.printmsg

tmp_dir = '/tmp'

# Create a test file then create a temp file that can update that
test_file = '/SmartBird/testing.test'
test_file_basename = test_file.split('/')[-1]

# FIXME Should also work if the file does not already exist
with open(test_file, 'w') as f:
    f.write('Testing')

my_temp = temp_file.create(test_file)
debug("my_temp: " + repr(my_temp))

with open(my_temp, 'w') as f:
    f.write('Testing')

check = 'Path and prefix'
assert my_temp.startswith('/tmp/' + test_file_basename), check
good(check)

check = 'Suffix'
assert my_temp.endswith('.tmp'), check
good(check)

check = 'create()'
try:
    with open(my_temp) as f:
        assert f.read() == 'Testing', check
except OSError:
    # FIXME [Errno 2] ENOENT
    raise AssertionError(check)

good(check)

try:
    remove(my_temp)
except:
    pass

check = 'install()'
my_temp = temp_file.create(test_file)
with open(my_temp, 'w') as f:
    f.write('Testing')

temp_file.install(my_temp, test_file)

with open(test_file) as f:
    assert f.read() == 'Testing', check
good(check)

# Clean up
try:
    remove(test_file)
except:
    pass

try:
    remove(temp_file)
except:
    pass