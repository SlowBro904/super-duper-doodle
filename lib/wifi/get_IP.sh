#!/bin/bash
if [ $# -eq 0 ]; then
    IFACE="wlan0"
else
    IFACE="${1}"
fi

ifconfig $IFACE | grep 'inet ' | awk '{print $2;}'