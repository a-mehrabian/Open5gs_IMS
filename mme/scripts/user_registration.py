import os
import csv
import subprocess
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

if len(sys.argv) < 2:
    print("Error: ENV_PATH argument is missing.")
    print("Usage: python script.py <path_to_env_file>")
    exit(1)

ENV_PATH = sys.argv[1]
load_dotenv(ENV_PATH)

MNC = os.getenv('MNC')
MCC = os.getenv('MCC')
WEBUI_IP = os.getenv('WEBUI_IP')
PYHSS_IP = os.getenv('PYHSS_IP')
OSMOHLR_IP = 'osmohlr'

WEBUI_PORT = 3000
PYHSS_PORT = 8082
OSMOHLR_PORT = 4258

script_path = Path(__file__).parent

required_scripts = ['hss_registration.sh', 'osmohlr_registration.sh', 'pyHss_registration.sh']
for script in required_scripts:
    if not (script_path / script).is_file():
        print(f"Error: '{script}' not found in script directory.")
        exit(1)

def is_imsi_registered(imsi):
    url = f'http://{PYHSS_IP}:{PYHSS_PORT}/subscriber/list?page=0&page_size=200'
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Unable to fetch IMSI data from PYHSS. HTTP status: {response.status_code}")
        return False

    subscribers = response.json()
    for subscriber in subscribers:
        if subscriber.get('imsi') == imsi:
            return True
    return False

csv_file = script_path / 'ue_list.csv'
if not csv_file.is_file():
    print("Error: 'ue_list.csv' not found in script directory.")
    exit(1)

try:
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            imsi = row['imsi']
            msisdn = row['msisdn']
            key = row['key']
            op = row['op']
            
            try:
                subprocess.check_call([str(script_path / 'hss_registration.sh'), WEBUI_IP, str(WEBUI_PORT), imsi, key, op, msisdn])
                subprocess.check_call([str(script_path / 'osmohlr_registration.sh'), OSMOHLR_IP, str(OSMOHLR_PORT), imsi, msisdn])
                if not is_imsi_registered(imsi):
                    subprocess.check_call([str(script_path / 'pyHss_registration.sh'), PYHSS_IP, str(PYHSS_PORT), imsi, msisdn, key, op, MCC, MNC])
                else:
                    print(f"IMSI {imsi} is already registered. Skipping pyHss_registration.")
            except subprocess.CalledProcessError as e:
                print(f"Error during script execution: {e}")
                exit(1)

except Exception as e:
    print(f"Error reading 'ue_list.csv': {e}")
    exit(1)
