#!/usr/bin/env python3
# pylint # {{{
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name, logging-not-lazy, logging-format-interpolation
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# }}}

import os
import sys
import datetime
import json
import paho.mqtt.client as mqtt
from mqtt_to_influx.parse_mqtt_data import ParseMqttData
from mqtt_to_influx.config import CONFIG
from mqtt_to_influx.parse_options import args
        

# The callback for when the mqtt_client receives a CONNACK response from the server.
def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected to server")

    print("Connecting configured mqtt topics with interpreters")
    for path in CONFIG['mqtt_topics']:
        try:
            mqtt_client.subscribe(path, qos = 0)
            __import__ ("mqtt_to_influx." + CONFIG['mqtt_topics'][path])
            callback_func = getattr(sys.modules["mqtt_to_influx." + CONFIG['mqtt_topics'][path]], "Process_mqtt_message")
            mqtt_client.message_callback_add(path, callback_func)
            print ("  Connected    {:<20}: {}".format(path, CONFIG['mqtt_topics'][path]))
        except Exception as e:
            print (f"  Error connecting: {e!r}")
            exit (2)
    # Subscribe all
    # mqtt_client.subscribe("/#")

def on_message(mqtt_client, userdata, msg):
    '''Default Handler for Processing message that aren't caught otherwhere'''
    print (F"Unrestiered topic: {msg.topic}")

if 'mqtt_topics' not in CONFIG:
    print ("Error no secion for 'mqtt_topics' found in pathconfig")
    exit (1)


def main():
    print ("Starting Daemon")

    mqtt_client = mqtt.Client()
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    #
    mqtt_client.connect(args.mqtt_host, args.mqtt_port, keepalive=60)
    #
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        print ("\b\b\nExit: user pressed control-c\n")
