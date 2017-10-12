#!/bin/bash
# Dynamic path
cd `dirname $0`

if [ $(./get_wifi_strength.sh) -eq 0 ]; then
    exit 1
fi