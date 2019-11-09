#!/bin/bash

SERVICE="mqtt-to-influx"
LIB_SYSD="/lib/systemd/system"

python3 setup.py sdist 
# pip install dist/mqtt-to-influx-0.0.1.dev10.tar.gz
pip install dist/${SERVICE}*tar.gz

test -e ${LIB_SYSD}/${SERVICE}.service || {
    # /usr/bin/passwordd install
    # passwordd install
    cp systemd/mqtt-to-influx.service ${LIB_SYSD}
}

systemctl enable $SERVICE
systemctl restart $SERVICE