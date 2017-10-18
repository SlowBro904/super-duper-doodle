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


def get_psk(ssid, password):
    psk = None
    # Try to encrypt the password
    raw, stderr = cmd("sudo wpa_passphrase \"" + ssid + "\" \"" + 
        password + "\"")[0:2]
    debug("wifi config() wpa_cli wpa_passphrase stderr: " + repr(stderr), 
        level = 1)
    
    for row in raw.split('\n'):
        match = re_search(r'^\s*psk=(.*)$', row)
        if match:
            psk = match.group(1)
            break
    
    return psk


def config(ssid, password = None, enc_type = None, hidden = False):
    '''Sets up our Wi-Fi network in /etc/wpa_supplicant/wpa_supplicant.conf'''
    timestamp = datetime.now().strftime('%Y-%m-%d.%H-%M')
    
    defaults()
    
    stderr = cmd("sudo wpa_cli ap_scan 1")[1]
    debug("wifi config() wpa_cli ap_scan 1 stderr: " + repr(stderr), level = 1)
    
    stderr = cmd("sudo wpa_cli add_network")[1]
    debug("wifi config() wpa_cli add_network stderr: " + repr(stderr), 
        level = 1)
    
    # Frequently-repeated command
    set_network = "sudo wpa_cli -i wlan0 set_network 0 "
    
    stderr = cmd(set_network + " ssid '\"" + ssid + "\"'")
    
    if hidden:
        stderr = cmd(set_network + " scan_ssid 1")[1]
        debug("wifi config() wpa_cli scan_ssid 1 stderr: " + repr(stderr), 
            level = 1)
    
    if not enc_type:
        stderr = cmd(set_network + " key_mgmt NONE")[1]
        debug("wifi config() wpa_cli key_mgmt NONE 1 stderr: " + repr(stderr), 
            level = 1)
    
    if enc_type == 'wep':
        # Don't use WEP boys and girls. We can't even encrypt the password.
        # FIXME Can't we?
        stderr = cmd(set_network + " key_mgmt NONE")[1]
        debug("wifi config() wpa_cli key_mgmt NONE stderr: " + repr(stderr), 
            level = 1)
        
        stderr = cmd(set_network + " wep_key0 " + get_psk(ssid, password))[1]
        debug("wifi config() wpa_cli wep_key0 stderr: " + repr(stderr), 
            level = 1)
        
        stderr = cmd(set_network + " wep_tx_keyidx 0")[1]
        debug("wifi config() wpa_cli wep_tx_keyidx stderr: " + repr(stderr), 
            level = 1)
    
    if enc_type in ['wpa', 'wpa2']:
        # TODO What if it is None
        stderr = cmd(set_network + " psk " + get_psk(ssid, password))[1]
        debug("wifi config() wpa_cli psk stderr: " + repr(stderr), level = 1)
    
    # TODO Also set the country code. Currently US.
    
    stderr = cmd("sudo wpa_cli enable_network 0")[1]
    debug("wifi config() wpa_cli enable_network stderr: " + repr(stderr), 
        level = 1)
    
    stderr = cmd("sudo wpa_cli select_network 0")[1]
    debug("wifi config() wpa_cli select_network stderr: " + repr(stderr), 
        level = 1)
    
    stderr = cmd("sudo wpa_cli save_config")[1]
    debug("wifi config() wpa_cli save_config stderr: " + repr(stderr), 
        level = 1)

    # Do a .after backup as well
    stderr = cmd("sudo cp " + conf_file + " " + conf_file + "." + timestamp + 
        ".after")[1]
    debug("wifi config() Backup config stderr: " + repr(stderr), level = 1)


def connect():
    '''Connects to the network wlan0 is configured for'''
    stderr = cmd("/etc/init.d/networking restart")[1]
    debug("connect(): " + repr(stderr), level = 1)


def ssid(iface = 'wlan0'):
    '''Returns the ssid'''
    stdout, stderr = cmd('sudo /SmartBird/lib/wifi/get_SSID.sh ' + iface)[0:2]
    debug("wifi/__init__.py ssid() stderr: " + repr(stderr), level = 1)
    return stdout


def isconnected():
    '''See if we are connected to the wlan0 Wi-Fi network'''
    # The [2] from cmd() is the exit status
    return cmd('sudo /SmartBird/lib/wifi/get_wifi_connected.sh')[2] == 0


def ip(iface = 'wlan0'):
    '''Returns the IP of the interface'''
    return cmd('sudo /SmartBird/lib/wifi/get_IP.sh ' + iface)[0]


def AP_sec_type(ssid):
    '''Takes an access point SSID, returns the security type'''
    return all_APs()[ssid][2]


def conn_strength():
    '''The strength of our wlan0 connection'''
    return cmd('sudo /SmartBird/lib/wifi/get_conn_strength.sh')[0]


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
    '''Returns a list of all SSIDs , sorted by signal strength'''
    temp_ssids1 = list()
    for ssid, values in all_APs().items():
        sig = values[0]
        temp_ssids1.append([ssid, sig])
    
    # Sort by signal strength
    # TODO Can we just overwrite the ssid var instead of creating temp_ssidsX?
    temp_ssids2 = sorted(temp_ssids1, key = lambda x: x[1], reverse = True)
    
    ssids = list()
    for ssid_combo in temp_ssids2:
        ssid = ssid_combo[0]
        ssids.append(ssid)

    return ssids