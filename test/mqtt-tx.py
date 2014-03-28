# demonstration of python + mqtt (mosquito): sending
# http://mosquitto.org/documentation/python/
#
# alternative: mosquitto_pub -t "mqtttest" -m "hello world"

import mosquitto
import time
import sys

def on_message(mosq, obj, msg):
    print "Received\t'%s' | topic '%s' qos%d" %(msg.topic, msg.payload, msg.qos)

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

def stop():
    print "Disconnecting..."
    mqttclient.disconnect()
    sys.exit()

try:
    while True:
        msg="{x:5,y:10,o:90,d:35}"
        topic="mqtttest"
        qos=1
        print "Publishing '%s' to topic '%s', qos%d" %(msg, topic, qos)
        mqttclient.publish(topic, msg, qos)
        if (mqttclient.loop() != 0):
            print "<Network Disconnect/Error>"
            stop()
        time.sleep(1)
except KeyboardInterrupt:
    stop()
