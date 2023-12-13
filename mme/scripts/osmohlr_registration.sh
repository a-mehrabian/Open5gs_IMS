#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 TELNET_SERVER TELNET_PORT UE_IMSI"
    exit 1
fi


TELNET_SERVER=$1
TELNET_PORT=$2
UE_IMSI=$3


(echo "enable"; echo "subscriber imsi $UE_IMSI create") | docker exec -i ${TELNET_SERVER} telnet localhost ${TELNET_PORT}

exit 0


#./mme/scripts/osmohlr_registration.sh osmohlr 4258 001010000000001