#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 TELNET_SERVER TELNET_PORT UE_IMSI UE_MSISDN"
    exit 1
fi


TELNET_SERVER=$1
TELNET_PORT=$2
UE_IMSI=$3
UE_MSISDN=$4


(echo "enable"; echo "subscriber imsi $UE_IMSI create"; echo "subscriber imsi $UE_IMSI update msisdn $UE_MSISDN") | docker exec -i ${TELNET_SERVER} telnet localhost ${TELNET_PORT}

exit 0


#./mme/scripts/osmohlr_registration.sh osmohlr 4258 001010000000001 00101