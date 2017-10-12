import lib.debugging
from wifi import Cell
from lib.cmd import cmd
from lib.config import config

# TODO Do I need?
debug = lib.debugging.printmsg
testing = lib.debugging.testing

def config(ssid, passphrase = None, enc_type = None, hidden = False):
    '''Sets up our Wi-Fi network in /etc/wpa_supplicant/wpa_supplicant.conf'''
    # Backup and set defaults
    timestamp = datetime.now().strftime('%Y-%m-%d.%H-%M')
    cmd("cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf." + timestamp + ".before")
    cmd("cat /etc/wpa_supplicant/wpa_supplicant.empty.conf > /etc/wpa_supplicant/wpa_supplicant.conf")
        
    network = cmd("wpa_cli -i wlan0 add_network")[0]
    
    # Repeated command
    set_network = "wpa_cli -i wlan0 set_network " + network
    
    cmd(set_network + " ssid '\"" + ssid + "\"'")
    
    if hidden:
        cmd(set_network + " scan_ssid 1")
    
    if not enc_type:
        cmd(set_network + " key_mgmt NONE")
        cmd(set_network + " priority 100")
        
    if enc_type == 'WEP':
        # Don't use WEP boys and girls. We can't even encrypt the passphrase.
        cmd(set_network + " key_mgmt NONE")
        cmd(set_network + " wep_key0 " + psk)
        cmd(set_network + " wep_tx_keyidx 0")
    
    if enc_type == 'WPA':
        # Encrypted passphrase
        raw = cmd("wpa_passphrase \"" + ssid + "\" \"" + passphrase + "\"")[0]
        for row in # FINISH
        
root@raspberrypi:/SmartBird/lib# wpa_passphrase "Be:my:guest" "Guest:my:be"
network={
        ssid="Be:my:guest"
        #psk="Guest:my:be"
        psk=1f9a05de335e74e3edcc5950e6f8cc349fecbb3d1f44bb2db8862567f4db24ec
}
root@raspberrypi:/SmartBird/lib# wpa_passphrase "Be:my:guest" "Guest:my:be" | grep "^        psk="
root@raspberrypi:/SmartBird/lib# wpa_passphrase "Be:my:guest" "Guest:my:be" 2>&1 | grep "^        psk="
root@raspberrypi:/SmartBird/lib# wpa_passphrase "Be:my:guest" "Guest:my:be" 2>&1 | grep "^\tpsk="
root@raspberrypi:/SmartBird/lib# wpa_passphrase "Be:my:guest" "Guest:my:be" 2>&1 | grep "^\s*psk="
        psk=1f9a05de335e74e3edcc5950e6f8cc349fecbb3d1f44bb2db8862567f4db24ec
root@raspberrypi:/SmartBird/lib#

        cmd(set_network + " psk " + psk)
    
    # TODO Also set the country code. Currently US.
    
    cmd("wpa_cli enable_network " + network)
    cmd("wpa_cli save_config")
    cmd("cp /etc/wpa_supplicant/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf." + timestamp + ".after")


def connect():
    '''Connects to the network wlan0 is configured for'''
    cmd("/etc/init.d/networking restart")


def ssid(iface = 'wlan0'):
    '''Returns the ssid'''
    return cmd('sudo lib/wifi/get_SSID.sh ' + iface)[0]


def isconnected():
    '''See if we are connected to the wlan0 Wi-Fi network'''
    return cmd('lib/wifi/get_wifi_connected.sh')[1] == 0


def ip(iface = 'wlan0'):
    '''Returns the IP of the interface'''
    return cmd('lib/wifi/get_IP.sh ' + iface)[0]


def AP_sec_type(ssid):
    '''Takes an access point SSID, returns the security type'''
    return all_APs[ssid][2]


def conn_strength():
    '''The strength of our wlan0 connection'''
    return cmd('lib/wifi/get_conn_strength.sh')[0]


def all_APs(iface = 'wlan0'):
    '''Returns a dictionary of visible access points.

    Keys are the SSIDs. Values are a list: signal, encryption (True/False), and
    encryption type (if any).
    '''
    all_APs = dict()
    for AP in Cell.all(iface):
        ssid, sig, enc = AP.ssid, AP.signal, AP.encrypted
        
        # Skip hidden APs
        if not ssid:
            continue
        
        try:
            enc_type = AP.encryption_type
        except AttributeError:
            enc_type = None
        
        all_APs[ssid] = [sig, enc, enc_type]
    
    return all_APs


def all_SSIDs():
    '''A set of all SSIDs sorted by signal strength'''
    ssids = list()
    for AP, values in all_APs().items():
        sig = values[0]
        ssids.append([ssid, sig])
    
    # Sort by signal strength
    return sorted(all_APs, key=lambda x: x[1])