import json
import os
import time
import paramiko
import threading

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def write_json_file(file_path, data):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

def read_remote_file(host, username, password, file_path):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password)
        sftp_client = client.open_sftp()
        remote_file = sftp_client.file(file_path, 'r')
        file_contents = json.load(remote_file)
        remote_file.close()
        client.close()
        return file_contents
    except Exception as e:
        print(f"Error reading remote file {file_path} from {host}: {e}")
        return None

def main(config_file, result_file):
    last_timestamps = {}
    while True:
        if not os.path.exists(config_file):
            print("Error: merger config does not exist")
            time.sleep(2)
            continue

        config = read_json_file(config_file)
        if config is None:
            print("Error reading merger config")
            time.sleep(2)
            continue

        all_data = []

        for server, details in config.items():
            if details['host'] == 'localhost':
                data = read_json_file(details['inputFile'])
            else:
                data = read_remote_file(details['host'], details['user'], details['pass'], details['inputFile'])

            if data and 'timestamp' in data:
                if server in last_timestamps and last_timestamps[server] == data['timestamp']:
                    continue            
                all_data.append(data)
                last_timestamps[server] = data['timestamp']

        all_data.sort(key=lambda x: x['timestamp'])

        if os.path.exists(result_file):
            existing_data = read_json_file(result_file)
            if existing_data:
                if existing_data[-1] == "]":
                    existing_data = existing_data[:-1] + ","
                existing_data.extend(all_data)
                write_json_file(result_file, existing_data)
        else:
            with open(result_file, 'w') as f:
                f.write('[')
            write_json_file(result_file, all_data)

        time.sleep(2)

if __name__ == "__main__":
    #if len(sys.argv) != 3:
    #    print("Usage: python script.py <path_to_mergerConfig.json> <path_to_merged_result.json>")
    #    sys.exit(1)

    #config_file_path = sys.argv[1]
    #result_file_path = sys.argv[2]

    config_file_path = "/home/ali/dev/Humanitas/open5gs_ims/srslte/scripts/mergerConfig.json"
    result_file_path = "/home/ali/dev/Humanitas/open5gs_ims/srslte/scripts/merged_result.json"

    main(config_file_path, result_file_path)
