#!/bin/bash
# Dynamic path
cd `dirname $0`

grep Serial /proc/cpuinfo | awk '{print $NF;}' | sed 's|^0*||;'