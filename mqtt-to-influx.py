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
import configargparse
import json
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient

def parseOptions():
    '''Parse the commandline options'''

    path_of_executable = os.path.realpath(sys.argv[0])
    folder_of_executable = os.path.split(path_of_executable)[0]
    full_name_of_executable = os.path.split(path_of_executable)[1]
    name_of_executable = full_name_of_executable.rstrip('.py')

    config_files = [os.environ['HOME']+'/.config/%s.conf' % name_of_executable,
                    folder_of_executable +'/%s.conf'     % name_of_executable]
    parser = configargparse.ArgumentParser(
            default_config_files = config_files,
            description=name_of_executable, ignore_unknown_config_file_keys=True)

    parser.add('-c', '--my-config',  is_config_file=True, help='config file path')
    parser.add_argument('--verbose', '-v', action="count", default=0, help='Verbosity')
    parser.add_argument('--influx_db_name',             default="")
    parser.add_argument('--influx_db_user',             default="")
    parser.add_argument('--influx_db_password',         default="")
    parser.add_argument('--influx_db_host',             default="")
    parser.add_argument('--influx_db_port',             default=8086)
    parser.add_argument('--mqtt_user',                  default="")
    parser.add_argument('--mqtt_password',              default="")
    parser.add_argument('--mqtt_host',                  default="")
    parser.add_argument('--mqtt_port',                  default=1883)

    parser.add_argument('--quiet',         '-q'   , default=False, action="store_true")

    # parser.add_argument(dest='access_token'   )

    return parser

# The callback for when the mqtt_client receives a CONNACK response from the server.
def on_connect(mqtt_client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqtt_client.subscribe("/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(mqtt_client, userdata, msg):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # print (msg.topic.split("/"))
    if (msg.topic.split("/")[1] in ('sensor', 'luefter')):
        device_name = msg.topic.split("/status/")[0].lstrip("/").replace("/",".")
        device_key  = msg.topic.split("/status/")[1]
        topic_dotted = msg.topic.replace("/",".").lstrip(".")
        topic_unders = msg.topic.replace("/","_").lstrip("_")
        payload_dec  = msg.payload.decode()
        # print ('dev_name: %s - key: %s - value: %s' % (device_name, device_key, payload_dec))
        json_body = [
            {
                "measurement": str(device_name),
                "tags": {
                    "friendly_name": str(device_key)
                    # "friendly_name": str(device_name),
                    # str(device_key): str(payload_dec)
                    # str(device_key): "x"
                },
                "fields": {
                    "value": float(payload_dec)
                }
            }
        ]
        influx_client.write_points(json_body)
    elif ((msg.topic.split("/")[1] in ('homegear')) and (msg.topic.split("/")[3] in ('jsonobj'))):
          # 1 "Entkleide"
          # 2 "Wohnzimmer"
          # 3 "Kueche vorn"
          # 4 "Kueche hinten"
          # 5 "Gaestezimmer"
          # 6 "Bad"
        devices=[" ", "Entkleide" , "Wohnzimmer" , "Kueche vorn" , "Kueche hinten" , "Gaestezimmer" , "Bad"]
        device_num   = msg.topic.split("/")[4]
        device_name  = devices[int(device_num)]
        # print ('Message: %s - %s - %s' % (current_time, topic_dotted, payload_dec))
        # print ('dev_num: %s: %s ' % (device_num, device_name))
        payload_json = json.loads(msg.payload.decode())

        # print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        for (k,v) in payload_json.items():
            # print ("key: %s - value: %s" % (k,v))
            payload_json[k]=float(v)
            # print ("key: %s - value: %s" % (k,payload_json[k]))
        # print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        try:
            json_body = [
                    {
                    "measurement": str(device_name),
                    "fields": payload_json 
                }
            ]
            # print(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
            # print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))

            influx_client.write_points(json_body)
        except Exception as e:
            print (str(e))
        
    # > CREATE DATABASE openhab_db
    # > CREATE USER admin WITH PASSWORD 'SuperSecretPassword123+' WITH ALL PRIVILEGES
    # > CREATE USER openhab WITH PASSWORD 'AnotherSuperbPassword456-'
    # > CREATE USER grafana WITH PASSWORD 'PleaseLetMeRead789?'
    # > GRANT ALL ON openhab_db TO openhab
    # > GRANT READ ON openhab_db TO grafana
    # drop database home_db
    # create database home_db
    # grant all on home_db to writer
    # grant read on home_db to grafana
        

args = parseOptions().parse_args()


influx_client = InfluxDBClient(args.influx_db_host, args.influx_db_port, database=args.influx_db_name)
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(args.mqtt_host, args.mqtt_port, keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqtt_client.loop_forever()
