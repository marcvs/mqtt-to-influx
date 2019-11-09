#!/bin/bash

SERVICE="mqtt-to-influx"
LIB_SYSD="/lib/systemd/system"
INSTALL=pip
USER=mqttinflux

PIP=`which pip3`
test -z $PIP && {
    PIP=`which pip`
    test -z $PIP && {
        echo "pip not found.\n    apt-get install python3-pip"
        exit 1
    }
}

echo "pip: ${PIP}"


# test -d dist && {
#     echo "You should remove the dist dir first"
#     exit 1
# }

python3 setup.py sdist 
FULLNAME=`python3 setup.py --fullname`

echo -e "\nDone building ${FULLNAME}\n"

# IF we're root, we go and install
[ ${UID} == 0 ] && {
    ${PIP} install dist/${FULLNAME}*tar.gz
    useradd -m ${USER}
    RV=$?
    case "$RV" in
        0-8) echo "Error creating user"; exit 1;;
        10-14) echo "Error creating user"; exit 1;;
    esac

    test -e ${LIB_SYSD}/${SERVICE}.service && {
        diff -q systemd/mqtt-to-influx.service ${LIB_SYSD} >/dev/null || {
            rm -f ${LIB_SYSD}/${SERVICE}.service
        }
    }
    test -e ${LIB_SYSD}/${SERVICE}.service || {
        cp systemd/mqtt-to-influx.service ${LIB_SYSD}
        systemctl daemon-reload
    }
    systemctl enable $SERVICE
    systemctl restart $SERVICE
}

# else we print the necessary steps
[ ${UID} == 0 ] || {
    echo -e "\nPlease run the following commands as root:\n"

    echo "    ${PIP} install dist/${FULLNAME}*tar.gz"

    echo "    useradd -m ${USER}"
    test -e ${LIB_SYSD}/${SERVICE}.service && {
        diff -q systemd/mqtt-to-influx.service ${LIB_SYSD} >/dev/null || {
            echo "    rm -f ${LIB_SYSD}/${SERVICE}.service"
            echo "    cp systemd/mqtt-to-influx.service ${LIB_SYSD}"
        }
    }
    echo "    systemctl enable $SERVICE"
    echo "    systemctl restart $SERVICE"
    echo -e "\nto install the software as a daemon"
}
