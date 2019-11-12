#!/bin/bash

SERVICE="mqtt-to-influx"
LIB_SYSD="/lib/systemd/system"
SYSD_SERVICE=systemd/mqtt-to-influx.service
USER=mqttinflux
ETC_CONFIG=/etc/mqtt-to-influx

PIP=`which pip3`
test -z $PIP && {
    PIP=`which pip`
    test -z $PIP && {
        echo -e "pip not found.\n    =>  apt-get install python3-pip"
        exit 1
    }
}

echo "pip: ${PIP}"


# test -d dist && {
#     echo "You should remove the dist dir first"
#     exit 1
# }

echo "Building sdist"
python3 setup.py sdist  > build.log 2>&1

FULLNAME=`python3 setup.py --fullname`

echo -e "\nDone building ${FULLNAME}\n"

# IF we're root, we go and install
[ ${UID} == 0 ] && {
    echo "Installing ${SERVICE} via ${PIP}"
    ${PIP} install dist/${FULLNAME}*tar.gz
    useradd -m ${USER}
    RV=$?
    case "$RV" in
        0-8) echo "Error creating user"; exit 1;;
        10-14) echo "Error creating user"; exit 1;;
    esac


    test -d ${ETC_CONFIG} || {
        echo "Creating ${ETC_CONFIG} and copying defaults there"
        mkdir -p ${ETC_CONFIG}
        cp mqtt-to-influx.*conf ${ETC_CONFIG}
        chown -R ${USER} ${ETC_CONFIG}
    }

    test -e ${LIB_SYSD}/${SERVICE}.service && {
        diff -q ${SYSD_SERVICE} ${LIB_SYSD} >/dev/null || {
            echo "Preparing systemd service for update"
            rm -f ${LIB_SYSD}/${SERVICE}.service
        }
    }
    test -e ${LIB_SYSD}/${SERVICE}.service || {
        echo "Installing systemd service"
        cp ${SYSD_SERVICE} ${LIB_SYSD}/${SERVICE}.service
        systemctl daemon-reload
    }
    echo "Restarting service"
    systemctl enable $SERVICE
    systemctl restart $SERVICE
    echo "Done"
}

# else we print the necessary steps
[ ${UID} == 0 ] || {
    echo -e "\nPlease run the following commands as root:\n"

    echo "    ${PIP} install dist/${FULLNAME}*tar.gz"

    echo "    useradd -m ${USER}"
    test -e ${LIB_SYSD}/${SERVICE}.service && {
        diff -q ${SYSD_SERVICE} ${LIB_SYSD} >/dev/null || {
            echo "    rm -f ${LIB_SYSD}/${SERVICE}.service"
            echo "    cp ${SYSD_SERVICE} ${LIB_SYSD}/${SERVICE}.service"
        }
    }
    echo "    systemctl enable $SERVICE"
    echo "    systemctl restart $SERVICE"
    echo -e "\nto install the software as a daemon"
}
