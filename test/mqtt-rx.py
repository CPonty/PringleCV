# demonstration of python + mqtt (mosquito): receiving
# http://mosquitto.org/documentation/python/
#
# alternative:mosquitto_sub -t "mqtttest"

import mosquitto
import time
import sys

def on_message(mosq, obj, msg):
    print "Received\t'%s' | topic '%s' qos%d" %(msg.payload, msg.topic, msg.qos)

def on_connect(mosq, obj, rc):
    print "Connected\tstatus %d" %(rc)

def on_disconnect(mosq, obj, rc):
    print "Disconnected\tstatus %d" %(rc)

def on_subscribe(mosq, obj, mid, qos_list):
    print "Subscribed\tmid %s" %(mid)

def on_unsubscribe(mosq, obj, mid):
    print "Unsubscribed\tmid %s" %(mid)

def on_publish(mosq, obj, mid):
    print "Published\tmid %s" %(mid)

mqttclient = mosquitto.Mosquitto() #no client id = randomly generated

mqttclient.on_message = on_message
mqttclient.on_connect = on_connect
mqttclient.on_disconnect = on_disconnect
mqttclient.on_subscribe = on_subscribe
mqttclient.on_unsubscribe = on_unsubscribe
mqttclient.on_publish = on_publish

ip="127.0.0.1"
port=1883
print "Connecting to %s:%d" %(ip, port)
mqttclient.connect(ip, port)

topic="mqtttest"
qos=1
print "Subscribing to topic '%s', qos%d" %(topic, qos)
mqttclient.subscribe(topic, qos)

def stop():
    print "Disconnecting..."
    mqttclient.disconnect()
    sys.exit()

try:
    mqttclient.loop_forever()
except KeyboardInterrupt:
    stop()
