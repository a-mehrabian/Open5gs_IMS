import time
import json
import os

# Global variables
input_file = 'enb_report.json'
output_file = 'output.json'
max_file_size = 99 # in kilobytes
file_counter = 0

def read_last_n_lines(file, n=100):
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
    start, foundMetric = False, False
    json_content = ''
    for line in lines:
        if line.startswith('{'):
            if start:
                json_content = ''
                foundMetric = False
            start = True            
        if start:
            json_content += line
            if '"type": "metrics"' in line:
                foundMetric = True
            elif line.startswith('}'):
                if foundMetric:
                    return json_content
                else:
                    json_content = ''
                    start = False
                    foundMetric = False
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
        if os.path.getsize(input_file) > max_file_size * 1024:
            directory, filename = os.path.split(input_file)

            parts = filename.split('.', 1)
            file_to_remove = os.path.join(directory, f"{parts[0]}.{file_counter}.json")

            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)
                print(f"Removed file: {file_to_remove}")

            file_counter += 1

            input_file = os.path.join(directory, f"{parts[0]}.{file_counter}.json")
            print(f"New input_file name: {input_file}")
    except Exception as e:
        pass

def main(config_file='parserConfig.json'):
    global input_file, output_file

    while True:
        cleanup()
        if not os.path.exists(input_file):
            print(f"Error: {input_file} not found.")
            time.sleep(1)
            continue

        lines = read_last_n_lines(input_file)
        json_content = extract_json_content(lines)

        if json_content:
            try:                
                content = json.loads(json_content)  # Validate JSON
                try:
                    if len(content['cell_list']) > 0 and \
                        len(content['cell_list'][0]['cell_container']['ue_list']) > 0 and \
                            (content['cell_list'][0]['cell_container']['ue_list'][0]['ue_container']['ul_pusch_rssi'] != 0.0 and \
                                content['cell_list'][0]['cell_container']['ue_list'][0]['ue_container']['ul_pucch_rssi'] != 0.0):
                        #if os.path.exists(config_file):
                        #    with open(config_file, 'r') as file:
                        #        config = json.load(file)
                        #        if config.get("classification", "") != "off":
                        #            write_output(json_content, config.get("outPutFileName", output_file), append=True)
                        write_output(json_content, output_file, append=False)
                except Exception as e:
                    pass
            except json.JSONDecodeError:
                pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]
    #input_file = "/home/ali/dev/Humanitas/srsRAN_tmsi/srsenb/enb_report.json"
    #output_file = "/home/ali/dev/Humanitas/srsRAN_tmsi/srsenb/output.json"
    #config_file = "/home/ali/dev/Humanitas/open5gs_ims/srslte/parserConfig.json"
    main()
