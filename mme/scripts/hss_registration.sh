#!/bin/bash

if [ "$#" -ne 6 ]; then
    echo "Usage: $0 SERVER_ADDRESS SERVER_PORT UE_IMSI UE_KEY UE_OP UE_MSISDN"
    exit 1
fi

USER="admin"
PASS="1423"
SERVER_ADDRESS=$1
SERVER_PORT=$2
UE_IMSI=$3
UE_KEY=$4
UE_OP=$5
UE_MSISDN=$6


COOKIE_JAR="cookie.txt"
rm -f $COOKIE_JAR


extract_json_value() {
    key=$1
    echo $2 | sed -n "s/.*\"$key\":\"*\([^\",}]*\).*$/\1/p"
}


response=$(curl -s "http://$SERVER_ADDRESS:$SERVER_PORT/api/auth/csrf" \
  -H 'Accept: application/json, text/plain, */*' \
  -c $COOKIE_JAR \
  --compressed \
  --insecure)
csrfToken=$(extract_json_value "csrfToken" "$response")


login_response=$(curl -s "http://$SERVER_ADDRESS:$SERVER_PORT/api/auth/login" \
  -H 'Content-Type: application/json' \
  -b $COOKIE_JAR -c $COOKIE_JAR \
  -H "X-CSRF-TOKEN: $csrfToken" \
  --data-raw "{\"username\":\"$USER\",\"password\":\"$PASS\"}" \
  --compressed \
  --insecure)

#echo $login_response

response=$(curl -s "http://$SERVER_ADDRESS:$SERVER_PORT/api/auth/session" \
  -b $COOKIE_JAR -c $COOKIE_JAR \
  --compressed \
  --insecure)
authToken=$(extract_json_value "authToken" "$response")
csrfToken=$(extract_json_value "csrfToken" "$response")
#echo $response
#echo $authToken
#exit

curl -s "http://$SERVER_ADDRESS:$SERVER_PORT/api/db/Subscriber" \
  -H 'Content-Type: application/json' \
  -b $COOKIE_JAR -c $COOKIE_JAR \
  -H "X-CSRF-TOKEN: $csrfToken" \
  -H "Authorization: Bearer $authToken" \
  --data-raw "{\"imsi\":\"$UE_IMSI\",\"msisdn\":[\"$UE_MSISDN\"],\"security\":{\"k\":\"$UE_KEY\",\"amf\":\"8000\",\"op_type\":0,\"op_value\":\"$UE_OP\",\"op\":null,\"opc\":\"$UE_OP\"},\"ambr\":{\"downlink\":{\"value\":1,\"unit\":3},\"uplink\":{\"value\":1,\"unit\":3}},\"slice\":[{\"sst\":1,\"default_indicator\":true,\"session\":[{\"name\":\"internet\",\"type\":1,\"ambr\":{\"downlink\":{\"value\":1,\"unit\":3},\"uplink\":{\"value\":1,\"unit\":3}},\"qos\":{\"index\":9,\"arp\":{\"priority_level\":8,\"pre_emption_capability\":1,\"pre_emption_vulnerability\":1}}},{\"name\":\"ims\",\"type\":3,\"qos\":{\"index\":5,\"arp\":{\"priority_level\":1,\"pre_emption_capability\":1,\"pre_emption_vulnerability\":1}},\"ambr\":{\"downlink\":{\"value\":3850,\"unit\":1},\"uplink\":{\"value\":1530,\"unit\":1}},\"ue\":{},\"smf\":{},\"pcc_rule\":[\
  {\"qos\":{\"index\":1,\"arp\":{\"priority_level\":2,\"pre_emption_capability\":2,\"pre_emption_vulnerability\":2},\"mbr\":{\"downlink\":{\"value\":128,\"unit\":1},\"uplink\":{\"value\":128,\"unit\":1}},\"gbr\":{\"downlink\":{\"unit\":1},\"uplink\":{\"unit\":1}}}}]}]}]}" \
  --compressed \
  --insecure

rm -f $COOKIE_JAR

#./mme/scripts/hss_registration.sh 172.22.0.26 3000 991011234567895 8baf473f2f8fd09487cccbd7097c6862 11111111111111111111111111111111 00202