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
        device_name   = msg.topic.split("/status/")[0].lstrip("/").replace("/",".")
        friendly_name = msg.topic.split("/status/")[1]

        if friendly_name in ("log", "ip_status"):
            return None

        payload_dec  = msg.payload.decode()
        if int(CONFIG[configname].get('verbose', 0)) > 0:
            print (F"value: {payload_dec}")

        json_body = [
            {
                "measurement": str(device_name),
                "tags": {
                    "friendly_name": str(friendly_name)
                },
                "fields": {
                    "value": float(payload_dec)
                }
            }
        ]
        if CONFIG[configname].getboolean('do_write_to_influx'):
            influx_client.write_points(json_body)
        else: 
            if int(CONFIG[configname].get('verbose', 0)) > 1:
                print(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
        return None
