import os
from sys import path
import __main__ as main

topdir = os.getcwd().rsplit('/', 1)[1]
path.append('/' + topdir)

print("Starting " + main.__file__)

def good(msg):
    print("[SUCCESS] " + str(msg))