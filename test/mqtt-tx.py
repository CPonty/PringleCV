# demonstration of python + mqtt (mosquito): sending
# http://mosquitto.org/documentation/python/
#
# alternative: mosquitto_pub -t "mqtttest" -m "hello world"

import mosquitto
import time
import sys

def on_message(mosq, obj, msg):
    print "Received: '%s' (topic: '%s')" %(msg.topic, msg.payload)

def on_connect(mosq, obj, rc):
    print "Connected: status %d" %(rc)

def on_disconnect(mosq, obj, rc):
    print "Disconnected: status %d" %(rc)

def on_subscribe(mosq, obj, mid, qos_list):
    print "Subscribed: mid %s" %(mid)

def on_unsubscribe(mosq, obj, mid):
    print "Unsubscribed: mid %s" %(mid)

def on_publish(mosq, obj, mid):
    print "Published: mid %s" %(mid)

clientname="test-tx-client"
mqttclient = mosquitto.Mosquitto(clientname)

mqttclient.on_message = on_message
mqttclient.on_connect = on_connect
mqttclient.on_disconnect = on_disconnect
mqttclient.on_subscribe = on_subscribe
mqttclient.on_unsubscribe = on_unsubscribe
mqttclient.on_publish = on_publish

ip="127.0.0.1"
print "Connecting to %s:1883 as '%s'" %(ip, clientname)
mqttclient.connect(ip)

try:
    while True:
        mqttclient.loop()
        msg="hello world!"
        topic="mqtttest"
        qos=0
        print "Publishing message '%s' to topic '%s', qos%d" %(msg, topic, qos)
        mqttclient.publish(msg, topic, qos)
        time.sleep(1)
except KeyboardInterrupt:
    print "Disconnecting..."
    mqttclient.disconnect()
    sys.exit()
