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

        device_name = msg.topic.split("/STATE")[0].lstrip("/").replace("/",".")

        # make sure we have a json object
        try:
            payload_json = json.loads(msg.payload.decode())
        except json.decoder.JSONDecodeError:
            return None
        if int(CONFIG[configname].get('verbose', 0)) > 1:
            print ("payload_json: ")
            print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))

        try:
            for (k,v) in payload_json.items():
                # print ("key: %s - value: %s" % (k,v))
                payload_json[k]=float(v)
                # print ("key: %s - value: %s" % (k,payload_json[k]))
        except ValueError as e:
            pass

        # copy over selected values into new json 
        try:
            new_payload_json = {}
            for entry in ("POWER1", "POWER2"):
                new_payload_json[entry] = payload_json[entry]
        except ValueError as e:
            pass
        
        # Create final json_body for writing into influxdb
        try:
            json_body = [
                    { # sensor.4
                    "measurement": str(device_name),
                    "fields": new_payload_json 
                }
            ]
            # print(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
            # print(json.dumps(payload_json, sort_keys=True, indent=4, separators=(',', ': ')))
            if CONFIG[configname].getboolean('do_write_to_influx'):
                influx_client.write_points(json_body)
            if int(CONFIG[configname].get('verbose', 0)) > 0:
                print ("output json for storage in influx:")
                print(json.dumps(json_body, sort_keys=True, indent=4, separators=(',', ': ')))
            if int(CONFIG[configname].get('verbose', 0)) > 0:
                print("------\n")
        except Exception as e:
            print (F"{e!r}")

        return None

# print(F"{__name__} imported")
