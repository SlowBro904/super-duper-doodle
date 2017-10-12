#!/bin/bash
if [ $# -eq 0 ]; then
    IFACE="wlan0"
else
    IFACE="${1}"
fi

# Ignore any other value passed
if [ $IFACE = "wlan0" ]; then
    grep '^\s*ssid="' /etc/wpa_supplicant/wpa_supplicant.conf | sed 's|^\s*ssid="\(.*\)"|\1|;'
elif [ $IFACE = "wlan1" ]; then
    grep '^ssid=' /etc/hostapd/access_point.conf | sed 's|^ssid=||;'
fi