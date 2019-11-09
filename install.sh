#!/bin/bash

SERVICE="mqtt-to-influx"
LIB_SYSD="/lib/systemd/system"
INSTALL=pip

PIP=`which pip3`
test -z $PIP && {
    PIP=`which pip3`
    test -z $PIP && {
        echo "pip not found.\n    apt-get install python3-pip"
        exit 1
    }
}



test -d dist && {
    echo "You should remove the dist dir first"
    exit 1
}
python3 setup.py sdist 
# pip install dist/mqtt-to-influx-0.0.1.dev10.tar.gz
pip install dist/${SERVICE}*tar.gz

# test -e ${LIB_SYSD}/${SERVICE}.service || {
    # /usr/bin/passwordd install
    # passwordd install
test -e ${LIB_SYSD}/${SERVICE}.service && {
    rm -f ${LIB_SYSD}/${SERVICE}.service
}
cp systemd/mqtt-to-influx.service ${LIB_SYSD}

systemctl enable $SERVICE
systemctl restart $SERVICE
