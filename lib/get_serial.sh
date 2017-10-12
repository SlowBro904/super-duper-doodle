#!/bin/bash
grep Serial /proc/cpuinfo | awk '{print $NF;}' | sed 's|^0*||;'
