#!/bin/bash
find -name "*.sh" -exec chmod +x "{}" \; &>/dev/null
find -name "*.sh" -exec dos2unix "{}" \; &>/dev/null
find -name "*.py" -exec chmod +x "{}" \; &>/dev/null
find -name "*.py" -exec dos2unix "{}" \; &>/dev/null