# TODO Failover
import lib.debugging
from time import sleep
from hashlib import sha512
from binascii import hexlify
from json import dumps, loads
from lib.config import config
import paho.mqtt.client as mqtt
from lib.system import SystemCls

system = SystemCls()
debug = lib.debugging.printmsg
testing = lib.debugging.testing

class MQTTCls(object):
    def __init__(self):
        '''Setup our MQTT object'''       
        debug("mqtt.py __init__() start", level = 1)
        
        self.data = dict()
        self.resub = False
        
        device_name = config.conf['DEVICE_NAME']
        self.server = config.conf['MQTT_SERVER']
        self.port = int(config.conf['MQTT_PORT'])
        self.retries = config.conf['MQTT_RETRIES']
        self.timeout = config.conf['MQTT_TIMEOUT']
        username = config.conf['SERVICE_ACCOUNT_EMAIL']
        password = config.conf['SERVICE_ACCOUNT_PASSWORD']
        
        # Use the device name, the serial, then the version, for the root 
        # path. I'm including the device name and version so that we can have 
        # multiple devices and a newer version does not break the interface for 
        # clients not upgraded yet
        self.root_path = device_name + '/' + system.serial
        self.root_path += '/' + system.version
        
        # A normal client
        self.client = mqtt.Client()
        self.client.username_pw_set(username = username, password = password)
        self.client.on_message = self._on_message
        self.client.on_log = self._on_log
        debug("mqtt.py __init__() end", level = 1)
    
    
    def connect(self, retries = None):
        '''Connect to the MQTT broker'''
        if not retries:
            retries = self.retries
        
        for i in range(retries):
            if not self.client.connect(self.server, self.port, self.timeout):
                # FIXME Test this
                # FIXME Why do I have this?
                self.resub = True
            else:
                debug("mqtt.py connect() failed, retrying...", level = 1)
                break
        
        self.client.loop_start()
    
    
    def disconnect(self):
        '''Disconnect from the MQTT broker'''
        self.client.disconnect()
    
    
    def publish(self, topic, msg, retries = None):
        '''Publish a data update to an MQTT topic.
        
        Optionally don't require a login to the MQTT server.
        This is ideal for things such as ping.
        '''
        # FIXME Reimplement ping without login, enable signed updates
        if not retries:
            retries = self.retries
        
        self.sub(topic)
        
        in_topic = self.root_path + '/in/' + topic
        msg = dumps(msg)
        
        debug("mqtt.py publish() in_topic: " + repr(in_topic), level = 1)
        debug("mqtt.py publish() type(in_topic): " + repr(type(in_topic)),
                level = 1)
        debug("mqtt.py publish() msg: " + repr(msg), level = 1)
        debug("mqtt.py publish() type(msg): " + repr(type(msg)), level = 1)
        
        result = None
        for i in range(retries):
            debug("mqtt.py publish() retries i: " + repr(i), level = 1)
            result = self.client.publish(in_topic, msg)
            
            if result:
                debug("mqtt.py publish() publish result == True", level = 1)
                break
        
        return result
    
    
    def get(self, topic, retries = None):
        '''Gets any current data in an MQTT topic'''
        if not retries:
            retries = self.retries
        
        self.sub(topic)
        
        # The full topic would be device and serial and all that. Remove all
        # but the end topic name.
        topic = topic.split('/')[-1]
        
        msg = None
        for i in range(retries):
            # FIXME Test
            try:
                msg = self.data[topic]
                break
            except KeyError:
                debug("mqtt.py get() Can't find self.data['" + str(topic) + 
                        "']. Retrying.", level = 1)
                sleep(1)
        
        debug("mqtt.py get() msg: " + repr(msg), level = 1)
        return msg
    
    
    def _on_message(self, client, userdata, msg):
        '''Callback to collect messages as they come in'''
        # The full topic would be device and serial and all that. Remove all
        # but the end topic name.
        topic = msg.topic
        msg = msg.payload.decode('utf-8')
        debug("mqtt.py _on_message() topic @ start: " + repr(topic), level = 1)
        debug("mqtt.py _on_message() msg @ start: " + repr(msg), level = 1)
        
        topic = topic.split('/')[-1]
        
        # Remove outer JSON encoding
        msg, remt_sha = loads(msg)
        
        recv_msg_sha = hexlify(sha512(msg.encode('utf-8')).digest())
        
        # Remove the inner JSON encoding
        msg = loads(msg)
        
        # TODO I think this should be more clearly stated like this:
        # remt_sha = remt_sha.encode('utf-8)
        remt_sha = bytes(remt_sha, 'utf-8')
        
        if remt_sha == recv_msg_sha:
            debug("mqtt.py _on_message() remt_sha == recv_msg_sha", level = 1)
            
            self.data[topic] = msg
            
            debug("mqtt.py _on_message() self.data[topic]: '" +
                    str(self.data[topic]) + "'", level = 1)
        else:
            # FIXME ping, curr_client_ver, etc. are failing here yet not
            # failing in their execution as they should
            debug("mqtt.py _on_message() remt_sha != recv_msg_sha", level = 1)
            debug("mqtt.py _on_message() msg: '" + str(msg) + "'", level = 1)
            debug("mqtt.py _on_message() remt_sha: '" + str(remt_sha) + "'", 
                level = 1)
            debug("mqtt.py _on_message() recv_msg_sha: '" +
                str(recv_msg_sha) + "'", level = 1)
            
            # FIXME Else what? Hopefully re-request.
            pass
    
    
    def _on_log(self, client, userdata, level, buf):
        debug("Log userdata: " + repr(userdata), level = 1)
        debug("Log level: " + repr(level), level = 1)
        debug("Log buf: " + repr(buf), level = 1)
    
    
    def sub(self, topic, login = True, retries = None):
        '''Subscribes to an MQTT topic'''
        if not self.resub and topic in self.data:
            debug("mqtt.py sub() self.resub: " + repr(self.resub), level = 1)
            debug("mqtt.py sub() self.data: " + repr(self.data), level = 1)
            return
        
        if not retries:
            retries = self.retries
        
        out_topic = self.root_path + '/out/' + topic
        
        for i in range(retries):
            if self.client.subscribe(out_topic, qos = 1):
                debug("mqtt.py sub() Successfully subscribed to '" + 
                        str(out_topic) + "'", level = 1)
                # FIXME Don't set resub to false because we probably have other
                # topics. But if true resub everything in self.data and/or
                # maybe clear data and force a refetch. I think msg persistence
                # may be required except in cases like ping? But if we ping we
                # at least know our connection to the broker is good. We don't
                # care all that much to test from client through broker to
                # processing modules. We can test broker to processing modules
                # elsewhere.
                self.resub = False
                break
            else:
                debug("mqtt.py sub() Can't subscribe to '" + str(out_topic) + 
                        "'. Retrying.", level = 1)