#!/bin/bash
if ! whoami | grep -q root; then
    echo "ERROR: Must be run as root."
    exit
fi

# Dynamic path
cd `dirname $0`

echo "This sets up SmartBird and reboots. After the reboot it should be ready to go."
sleep 3

# TODO Silence this and capture failures as ERROR/WARNING

#apt-get purge fake-hwclock ntp wolfram-engine triggerhappy anacron logrotate dphys-swapfile xserver-common lightdm
#insserv -r x11-common

# Necessary packages
apt-get update
# FIXME Inside update_sys.py get_sys_updates() check whether we can apt-get dist-upgrade
apt-get --assume-yes dist-upgrade

apt-get --assume-yes install dnsmasq hostapd watchdog python3-gpiozero python3-smbus python3-smbus python3-dev i2c-tools python3-pip python3-pigpio rng-tools
#apt-get --assume-yes install ntpdate python-arrow python-picamera busybox-syslogd
#dpkg --purge rsyslog
apt-get autoremove --purge

pip3 install paho-mqtt wifi

#sudo apt-get install pypy pypy-dev pypy-pkg-resources pypy-setuptools
#curl -O https://bootstrap.pypa.io/get-pip.py
#pypy -mpip install paho-mqtt wifi pigpio

# FIXME Add specific commands not carte blanche root
gpasswd -a nobody sudo
gpasswd -a nobody gpio

# Install our custom files
cp -a boot /
cp -a etc /
#cp -a lib /
#cp -a var /

# FIXME Update MAC address in /etc/udev/rules.d/70*
# FIXME Daemons only listen on 1.1.1.1 AND setup firewall rules

update-rc.d ap defaults

# FIXME Time zone. tzselect is the command.
# You can make this change permanent for yourself by appending the line
# TZ='America/New_York'; export TZ
# to the file '.profile' in your home directory; then log out and log in again.
# Here is that TZ value again, this time on standard output so that you
# can use the /usr/bin/tzselect command in shell scripts:
# America/New_York


#update-rc.d hostapd disable
#systemctl daemon-reload
#systemctl enable hostapd-systemd

#sed -i "s|^ssid=.*\$|ssid=SmartBird$(./get_serial.sh)|;" /etc/hostapd/access_point.conf

# On the server side, run this:
# gpg --gen-key --batch gpg_batch.txt
# gpg --output .gnupg/support.pub.gpg --export
# gpg --export-ownertrust > .gnupg/support.ownertrust.gpg.txt
# gpg --import $SERIAL.pub.gpg
# gpg --import-ownertrust $SERIAL.ownertrust.gpg.txt

#GNUPGBATCH=$(mktemp /tmp/gpg_batch.XXXXX.tmp)
#cat gpg/batch.txt > $GNUPGBATCH
#sed -i "s|^Name-Real: .*\$|Name-Real: $(../common/get_serial.sh)|;" $GNUPGBATCH
#gpg --gen-key --batch $GNUPGBATCH
#rm -f $GNUPGBATCH
#gpg --output /root/.gnupg/$(../common/get_serial.sh).pub.gpg --export
#gpg --export-ownertrust > /root/.gnupg/$(../common/get_serial.sh).ownertrust.gpg.txt
#gpg --import gpg/support.pub.gpg
#gpg --import-ownertrust gpg/support.ownertrust.gpg.txt

# TODO On the remote side I need to jump through this hoop. Not sure why.
# gpg --recipient $(gpg --list-keys | grep -B1 $SERIAL | head -n1 | sed 's|^pub   2048R/\([^ ]*\) 20.*$|\1|;') --encrypt deleteme.2.txt

# Password.
# FIXME Change this so it's unique to the device
# FIXME Remove the pi username
# FIXME Add ListenAddress to sshd_config and web server
usermod -p $(echo smartbird | openssl passwd -1 -stdin) root

# FIXME For watchdog enable some other sensible settings in /etc/watchdog.conf such as temperature, ping, 

#hwclock -w
#update-rc.d hwclock.sh enable

## For a read-only filesystem
#rm -rf /var/lib/dhcp/ /var/run /var/spool /var/lock /etc/resolv.conf
#ln -s /tmp /var/lib/dhcp
#ln -s /tmp /var/run
#ln -s /tmp /var/spool
#ln -s /tmp /var/lock
#touch /tmp/dhcpcd.resolv.conf; ln -s /tmp/dhcpcd.resolv.conf /etc/resolv.conf
#rm /var/lib/systemd/random-seed
#ln -s /tmp/random-seed /var/lib/systemd/random-seed
#insserv -r bootlogs
#insserv -r console-setup

chown nobody -R /SmartBird
find /SmartBird -type f -name "*.py" -exec chmod 755 "{}" \;
find /SmartBird -type f -name "*.sh" -exec chmod 755 "{}" \;
find /SmartBird -type f -name "*.cgi" -exec chmod 755 "{}" \;
chown nobody /etc/wpa_supplicant/wpa_supplicant.conf

echo "The system will now reboot..."
sleep 3
reboot