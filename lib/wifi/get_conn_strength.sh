#!/bin/bash
grep wlan0 /proc/net/wireless | awk '{print $3;}' |sed 's|\.$||;'