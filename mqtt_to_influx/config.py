import os
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from pathlib import Path

# CONFIG = ConfigParser()
CONFIG = ConfigParser(interpolation=ExtendedInterpolation())
CONFIG.optionxform = lambda option: option

def reload():
    """Reload configuration from disk.

    Config locations, by priority (all values are merged. The last one
        overwrites earlier ones)
    $MQTT_TO_INFLUX_CONFIG
    /etc/mqtt-to-influx/mqtt-to-influx.pathconf
    ./mqtt-to-influx.pathconf
    ~/.config/mqtt-to-influx/mqtt-to-influx.pathconf
    """
    files = []

    filename = os.environ.get("MQTT_TO_INFLUX_CONFIG")
    if filename:
        files += [Path(filename)]

    files += [
        Path('/')/'etc'/'mqtt-to-influx'/'mqtt-to-influx.pathconf',
        Path.home()/'.config'/'mqtt-to-influx'/'mqtt-to-influx.pathconf',
        Path('./mqtt-to-influx.pathconf')
    ]

    CONFIG.read(files)

# Load config on import
reload()
