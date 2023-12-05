import time
import json
import os
import sys
import csv
import paramiko
import re

config = None
input_file = ''
output_file = ''
file_counter = 0
rnti_to_imsi = {}
ssh_client = None
rnti_to_tmsi_line_counter = 0
rnti_to_rnti_line_counter = 0
tmsi_to_imsi_line_counter = 0

def populateImsi():
    global ssh_client, config, rnti_to_imsi, rnti_to_tmsi_line_counter, rnti_to_rnti_line_counter, tmsi_to_imsi_line_counter

    writeIt = False
    newRnti = False
    
    rnti_to_tmsi_map = {}
    try:
        with open(config['rnti-to-tmsi-file'], 'r') as csvfile:
            
            reader = csv.DictReader(csvfile)
            _ = reader.fieldnames 
            for _ in range(rnti_to_tmsi_line_counter):
                next(reader, None)
            
            for row in reader:
                newRnti = True
                rnti_to_tmsi_map[row['rnti']] = row['tmsi']
                rnti_to_tmsi_line_counter += 1
    except Exception as e:
        print("error reading rnti-to-tmsi-file")
        print(str(e))
        sys.exit(1)
    
    rnti_to_rnti_map = {}
    try:
        with open(config['rnti-to-rnti-file'], 'r') as csvfile:
            
            reader = csv.DictReader(csvfile)
            _ = reader.fieldnames 
            for _ in range(rnti_to_rnti_line_counter):
                next(reader, None)            
            
            for row in reader:
                rnti_to_rnti_map[row['new_rnti']] = row['existing_rnti']
                rnti_to_rnti_line_counter += 1
    except Exception as e:
        print("error reading rnti-to-rnti-file")
        print(str(e))
        sys.exit(1)

    tmsi_to_imsi_map = {}
    try:
        if newRnti:
            mme_config = config['mme-server']
            if mme_config['server'] != 'localhost':
                if not ssh_client:
                    ssh_client = paramiko.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh_client.connect(mme_config['server'], username=mme_config['username'], password=mme_config['password'])
                
                sftp = ssh_client.open_sftp()
                remote_file = sftp.file(mme_config['tmsi-to-imsi-file'], 'r')
                
                reader = csv.DictReader(remote_file)
                _ = reader.fieldnames
                for _ in range(tmsi_to_imsi_line_counter):
                    next(reader, None)
                
                for row in reader:
                    tmsi_to_imsi_map[row['tmsi']] = row['imsi']
                    tmsi_to_imsi_line_counter += 1
                remote_file.close()
            else:
                with open(mme_config['tmsi-to-imsi-file'], 'r') as csvfile:
                    
                    reader = csv.DictReader(csvfile)
                    _ = reader.fieldnames
                    for _ in range(tmsi_to_imsi_line_counter):
                        next(reader, None)
                    
                    for row in reader:
                        tmsi_to_imsi_map[row['tmsi']] = row['imsi']
                        tmsi_to_imsi_line_counter += 1
    except Exception as e:
        print("error reading tmsi-to-imsi-file")
        print(str(e))
        sys.exit(1)
    
    for rnti, tmsi in rnti_to_tmsi_map.items():
        imsi = tmsi_to_imsi_map.get(tmsi)
        if imsi:
            writeIt = True
            rnti_to_imsi[rnti] = imsi
    for newRnti, exsRnti in rnti_to_rnti_map.items():
        currentImsi = rnti_to_imsi.get(exsRnti)
        if currentImsi:
            writeIt = True
            rnti_to_imsi[newRnti] = currentImsi

    try:
        if writeIt:
            with open(config['output-rnti-to-imsi-file'], 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['rnti', 'imsi'])
                for rnti, imsi in rnti_to_imsi.items():
                    writer.writerow([rnti, imsi])
    except Exception as e:
        print ("Error, writing to rnti-to-imsi.csv")
        print(str(e))
        sys.exit(1)


def read_last_n_lines(file, n=120):
    with open(file, 'rb') as f:
        f.seek(0, os.SEEK_END)
        filesize = f.tell()
        f.seek(max(filesize - 1024 * n, 0))
        lines = f.readlines()
        if len(lines) >= n:
            return [line.decode('utf-8') for line in lines[-n:]]
        else:
            f.seek(0)
            return [line.decode('utf-8') for line in f.readlines()]

def extract_json_content(lines):
    start, foundMetric, rnti = False, False, False
    ue_id = 0
    reach_rnti = 0
    json_content = ''
    do_imsi = config.get("add-imsi", True)
    for line in lines:
        if line.startswith('{'):
            if start:
                json_content = ''
                foundMetric = False
                ue_id = 0
                rnti = False
                reach_rnti = 0
            start = True            
        if start:
            #json_content += line
            if rnti:
                reach_rnti += 1
            if not foundMetric and '"type": "metrics"' in line:
                foundMetric = True
                json_content += line
                continue
            elif do_imsi and not rnti and '"ue_rnti":' in line:
                rnti = True
                reach_rnti = 0
                match = re.search(r'":\s*(\w+),', line)
                if match:
                    rnti = str(hex(int(match.group(1))))
                    json_content += '              "ue_rnti": "' + rnti + '",\n'
                    if rnti_to_imsi.get(rnti):
                        json_content += '              "ue_imsi": "' + rnti_to_imsi.get(rnti) + '",\n'
                    else:
                        json_content += '              "ue_imsi": "imsi-' + str(ue_id) + '",\n'
                ue_id += 1            
            elif do_imsi and rnti and reach_rnti > 20 and '"ue_container"' in line:
                rnti = False
                json_content += line
            elif line.startswith('}'):
                json_content += line
                if foundMetric:
                    return json_content
                else:
                    json_content = ''
                    start = False
                    foundMetric = False
            else:
                json_content += line
    return None

def write_output(data, output_file, append=False):
    if append:
        if data.endswith('\n'):
            data = data[:-1]

        if not os.path.exists(output_file):
            data = '[\n' + data + '\n'
        else:
            with open(output_file, 'rb+') as file:
                file.seek(-1, os.SEEK_END)
                if file.read(1) == b']':
                    file.seek(-2, os.SEEK_END)
                    file.truncate()
                    data = ',' + '\n' + data + '\n'
        
        data += ']'

    with open(output_file, 'a' if append else 'w') as file:
        file.write(data)

def cleanup():
    global input_file, file_counter

    try:
        directory, filename = os.path.split(input_file)
        parts = filename.split('.', 1)
        temp_file = os.path.join(directory, f"{parts[0]}.{file_counter + 1}.json")

        if os.path.exists(temp_file):            
            file_to_remove = os.path.join(directory, f"{parts[0]}.{file_counter - 1}.json")
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)
                print(f"Removed file: {file_to_remove}")
            
            file_counter += 1
            input_file = temp_file

    except Exception as e:
        print(str(e))
        pass

def main(config_file='parserConfig.json'):
    global input_file, output_file, config, rnti_to_imsi

    lastTimeStamp = 1.1

    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                config = json.load(file)
        else:
            print("missing parserConfig.json")
            sys.exit(1)
    except Exception as e:
        print("error, setting up config from parserConfig.json!")
        sys.exit(1)
    
    while True:
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found.")
            time.sleep(1)
            continue
        else:
            break

    while True:
        cleanup()

        lines = read_last_n_lines(input_file)
        json_content = extract_json_content(lines)

        if json_content:
            try:                
                content = json.loads(json_content)  # Validate JSON
                try:
                    if lastTimeStamp != content['timestamp']:
                        if len(content['cell_list']) > 0 and \
                            len(content['cell_list'][0]['cell_container']['ue_list']) > 0 and \
                                (content['cell_list'][0]['cell_container']['ue_list'][0]['ue_container']['ul_pusch_rssi'] != 0.0 and \
                                    content['cell_list'][0]['cell_container']['ue_list'][0]['ue_container']['ul_pucch_rssi'] != 0.0):
                            if config.get("add-imsi", True):
                                ue_id = 0
                                for ue in content['cell_list'][0]['cell_container']['ue_list']:
                                    imsi = rnti_to_imsi.get(ue['ue_container']['ue_rnti'])
                                    if ue['ue_container']['ue_imsi'] != imsi:                                        
                                        if not imsi:
                                            populateImsi()
                                            imsi = rnti_to_imsi.get(ue['ue_container']['ue_rnti'])
                                            if not imsi:
                                                imsi = 'Unknown'
                                        json_content = json_content.replace('"ue_imsi": "imsi-' + str(ue_id) + '"', '"ue_imsi": "' + imsi + '"')
                                    ue_id += 1
                                            
                            if config.get("appending", True):
                                write_output(json_content, config.get("appended-file-name", output_file), append=True)
                            write_output(json_content, output_file, append=False)
                    else:
                        time.sleep(1)
                    lastTimeStamp = content['timestamp']
                except Exception as e:
                    print (str(e))
                    pass
            except json.JSONDecodeError:
                print (str(e))
                pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file, output_file = sys.argv[1], sys.argv[2]
    
    #input_file = "/home/ali/dev/Humanitas/open5gs_ims/srslte/logs/enb_report5.json"
    #output_file = "/home/ali/dev/Humanitas/open5gs_ims/srslte/logs/output.json"
    #config_file = "/home/ali/dev/Humanitas/open5gs_ims/srslte/scripts/parserConfig.json"
    main()
