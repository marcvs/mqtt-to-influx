# pylint # {{{
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name, logging-not-lazy, logging-format-interpolation
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# pylint: disable=unused-argument
# }}}
import json
from mqtt_to_influx.config import CONFIG
from mqtt_to_influx.influx_client import influx_client

class Process_mqtt_message:
    def __init__(self, mqtt_client, userdata, msg):
        configname = __name__.split('.')[1]
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            print("processing: {: <30}{}".format(msg.topic, msg.payload.decode()))

          # 1 "Entkleide"
          # 2 "Wohnzimmer"
          # 3 "Kueche vorn"
          # 4 "Kueche hinten"
          # 5 "Gaestezimmer"
          # 6 "Bad"
        devices=[" ", "Entkleide" , "Wohnzimmer" , "Kueche vorn" , "Kueche hinten" , "Gaestezimmer" , "Bad"]
        device_num   = msg.topic.split("/")[4]
        device_name  = devices[int(device_num)]

        # make sure we have a json object
        try:
            payload_json = json.loads(msg.payload.decode())
        except json.decoder.JSONDecodeError:
            return None
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            print ("payload_json: ")
            print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))

        # print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
        try:
            for (k,v) in payload_json.items():
                payload_json[k]=float(v)
        except ValueError as e:
            pass

        try:
            json_body = [
                    {
                    "measurement": str(device_name),
                    "fields": payload_json 
                }
            ]
            # print(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
            # print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
            if CONFIG[configname].getboolean('do_write_to_influx'):
                influx_client.write_points(json_body)
            else: 
                if int(CONFIG[configname].get('verbose', 0)) > 1:
                    print(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        except Exception as e:
            print (str(e))

        return None
