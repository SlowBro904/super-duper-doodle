import lib.debugging
from wifi import Cell
from lib.cmd import cmd
from lib.config import config
from datetime import datetime
from re import search as re_search

# TODO Do I need?
debug = lib.debugging.printmsg
testing = lib.debugging.testing
# TODO Do I want to put this in the config?
conf_file = '/etc/wpa_supplicant/wpa_supplicant.conf'

    
def defaults():
    '''Backup the config and set defaults'''
    cmd("wpa_cli remove_network 0")

    timestamp = datetime.now().strftime('%Y-%m-%d.%H-%M')

    command = "cp " + conf_file + " " + conf_file + "." + timestamp + ".before"
    stderr = cmd(command)[1]
    debug("defaults() backup config command: " + repr(command), level = 1)
    debug("defaults() backup config stderr: " + repr(stderr), level = 1)

    # FIXME Change file name on GitHub
    command = "cp " + conf_file + ".defaults " + conf_file
    stderr = cmd(command)[1]
    debug("defaults() cat default config command: " + repr(command), level = 1)
    debug("defaults() cat default config stderr: " + repr(stderr), level = 1)



def config(ssid, passphrase = None, enc_type = None, hidden = False):
    '''Sets up our Wi-Fi network in /etc/wpa_supplicant/wpa_supplicant.conf'''
    # FIXME Can't ping after setting all this. See what I missed.
    timestamp = datetime.now().strftime('%Y-%m-%d.%H-%M')

    defaults()

    cmd("wpa_cli ap_scan 1")

    cmd("wpa_cli add_network")
    
    # Frequently-repeated command
    set_network = "wpa_cli set_network 0 "
    
    cmd(set_network + " ssid '\"" + ssid + "\"'")
    
    if hidden:
        cmd(set_network + " scan_ssid 1")
    
    if not enc_type:
        cmd(set_network + " key_mgmt NONE")
        
    if enc_type == 'WEP':
        # Don't use WEP boys and girls. We can't even encrypt the passphrase.
        # FIXME Can't we?
        cmd(set_network + " key_mgmt NONE")
        cmd(set_network + " wep_key0 " + psk)
        cmd(set_network + " wep_tx_keyidx 0")
    
    if enc_type == 'WPA':
        psk = passphrase
        # Try to encrypt the passphrase
        raw = cmd("wpa_passphrase \"" + ssid + "\" \"" + passphrase + "\"")[0]
        for row in raw.split('\n'):
            match = re_search(r'^\s*psk=(.*)$', row)
            if match:
                psk = match.group(1)
                break
        
        # TODO What if it fails to find any?
        cmd(set_network + " psk " + psk)
    
    # TODO Also set the country code. Currently US.
    
    # FIXME Do I need to also enable_network?
    cmd("wpa_cli select_network 0")
    cmd("wpa_cli save_config")

    # Do a .after backup as well
    cmd("cp " + conf_file + " " + conf_file + "." + timestamp + ".after")


def connect():
    '''Connects to the network wlan0 is configured for'''
    stderr = cmd("/etc/init.d/networking restart")[1]
    debug("connect(): " + repr(stderr), level = 1)


def ssid(iface = 'wlan0'):
    '''Returns the ssid'''
    return cmd('sudo lib/wifi/get_SSID.sh ' + iface)[0]


def isconnected():
    '''See if we are connected to the wlan0 Wi-Fi network'''
    # The [2] from cmd() is the exit status
    return cmd('sudo lib/wifi/get_wifi_connected.sh')[2] == 0


def ip(iface = 'wlan0'):
    '''Returns the IP of the interface'''
    return cmd('sudo lib/wifi/get_IP.sh ' + iface)[0]


def AP_sec_type(ssid):
    '''Takes an access point SSID, returns the security type'''
    return all_APs()[ssid][2]


def conn_strength():
    '''The strength of our wlan0 connection'''
    return cmd('sudo lib/wifi/get_conn_strength.sh')[0]


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
    for ssid, values in all_APs().items():
        sig = values[0]
        ssids.append([ssid, sig])
    
    # Sort by signal strength
    return sorted(ssids, key = lambda x: x[1], reverse = True)
