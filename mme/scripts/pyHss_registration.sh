#!/bin/bash


if [ "$#" -ne 6 ]; then
    echo "Usage: $0 PYHSS_IP PYHSS_PORT UE_IMSI UE_MSISDN UE_Ki UE_OPC"
    exit 1
fi

PYHSS_IP=$1
PYHSS_PORT=$2
UE_IMSI=$3
UE_MSISDN=$4
UE_Ki=$5
UE_OPC=$6


response=$(curl -s -X 'GET' \
  "http://$PYHSS_IP:$PYHSS_PORT/apn/list?page=0&page_size=200" \
  -H 'accept: application/json')


if [ "$response" = "[]" ]; then
    
    internet_response=$(curl -s -X 'PUT' \
      "http://$PYHSS_IP:$PYHSS_PORT/apn/" \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
        "apn": "internet",
        "apn_ambr_dl": 0,
        "apn_ambr_ul": 0
      }')

    
    internet_apn_id=$(echo $internet_response | jq '.apn_id')

    
    ims_response=$(curl -s -X 'PUT' \
      "http://$PYHSS_IP:$PYHSS_PORT/apn/" \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{
        "apn": "ims",
        "apn_ambr_dl": 0,
        "apn_ambr_ul": 0
      }')

    ims_apn_id=$(echo $ims_response | jq '.apn_id')
else
    
    internet_apn_id=$(echo $response | jq '.[] | select(.apn=="internet") | .apn_id')
    ims_apn_id=$(echo $response | jq '.[] | select(.apn=="ims") | .apn_id')
fi


auc_response=$(curl -s -X 'PUT' \
  "http://$PYHSS_IP:$PYHSS_PORT/auc/" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
    \"ki\": \"$UE_KI\",
    \"opc\": \"$UE_OPC\",
    \"amf\": \"8000\",
    \"sqn\": 0,
    \"imsi\": \"$UE_IMSI\"
  }")


auc_id=$(echo $auc_response | jq '.auc_id')

curl -X 'PUT' \
  "http://$PYHSS_IP:$PYHSS_PORT/subscriber/" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
    \"imsi\": \"$UE_IMSI\",
    \"enabled\": true,
    \"auc_id\": $auc_id,
    \"default_apn\": $internet_apn_id,
    \"apn_list\": \"$internet_apn_id,$ims_apn_id\",
    \"msisdn\": \"$UE_MSISDN\",
    \"ue_ambr_dl\": 0,
    \"ue_ambr_ul\": 0
  }"


curl -X 'PUT' \
  "http://$PYHSS_IP:$PYHSS_PORT/ims_subscriber/" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
    \"imsi\": \"$UE_IMSI\",
    \"msisdn\": \"$UE_MSISDN\",
    \"sh_profile\": \"string\",
    \"scscf_peer\": \"scscf.ims.mnc001.mcc001.3gppnetwork.org\",
    \"msisdn_list\": \"[$UE_MSISDN]\",
    \"ifc_path\": \"default_ifc.xml\",
    \"scscf\": \"sip:scscf.ims.mnc001.mcc001.3gppnetwork.org:6060\",
    \"scscf_realm\": \"ims.mnc001.mcc001.3gppnetwork.org\"
  }"


  #./mme/scripts/pyHss_registration.sh 172.22.0.18 8082 001010000000001 001001 00112233445566778899AABBCCDDEE01 00112233445566778899AABBCCDDEE00