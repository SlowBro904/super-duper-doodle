import lib.debugging
from time import sleep
from lib.mqtt import MQTTCls

debug = lib.debugging.printmsg
testing = lib.debugging.testing

mqtt = MQTTCls()

class CloudCls(object):
    def connect(self):
        '''Connect to our MQTT broker'''
        #try:
        return mqtt.connect()
        #except:
        #    warning = ("Cannot connect to our MQTT broker.",
        #                "('cloud.py', 'connect')")
        #    err.warning(warning)
        #    return False
    
    
    def isconnected(self):
        '''Ensure we can login'''
        return self.send('ping') == 'ack'
    
    
    def send(self, topic, msg = None):
        '''Send a message to a topic and gets the reply.
        
        For example, topic = 'door_status', message = 'up'
        '''
        debug("cloud.py send() topic: '" + str(topic) + "'", level = 1)
        debug("cloud.py send() msg: '" + str(msg) + "'", level = 1)
        
        # FIXME What if we only had a temporary burp at startup?
        # FIXME Some way, some how, check if we are connected and if not, raise
        # this error. I get into infinite recursion when I call
        # self.isconnected().
        #if not self.isconnected():
        #    raise RuntimeError
        
        # FIXME Get the exact exception type on failure so we 
        # can raise a RuntimeError
        #try:
        mqtt.publish(topic, msg)
        #except:
        #    # TODO If we get multiple send warnings only record one
        #    warning = ("Unable to send to the cloud. Topic: '",
        #                str(topic) + "', message: '" + str(message) + "'")
        #    raise RuntimeError(warning)
        
        # FIXME Tweak to something more appropriate and setup a config entry
        # FIXME Or better, check that we got return data somehow
        ## Delay for publish and return data
        #sleep(5)
        
        # Be aware that mqtt.get() returns a byte object
        result = mqtt.get(topic)
        
        debug("result: " + repr(result), level = 1)
        
        return result
        ## TODO This may be a bit cleaner if we try/except on the error
        ##   TypeError: can't convert 'NoneType' object to str implicitly
        #if result is not None:
        #    return result
# End of CloudCls

cloud = CloudCls()
cloud.connect()