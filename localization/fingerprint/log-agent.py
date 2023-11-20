import sys
import os
import json
import time

time_scan = 50 #sec

dir_path = os.path.dirname(os.path.realpath(__file__))

MAX_FILE_SIZE = 2 * (1024 ** 3)  # 2GB

def read_json_from_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def append_json_to_file(file_name, data):
    if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
        with open(file_name, 'w') as f:
            json.dump([data], f)
    else:
        with open(file_name, 'r+b') as f:
            f.seek(-1, os.SEEK_END)
            f.truncate()
            f.write(b', ' + json.dumps(data).encode() + b']')

def main():
    # input_file = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('INPUT_FILE', None)
    # output_file = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('OUTPUT_FILE', None)
    input_file = os.path.join(dir_path, "../../localization_stats.log")
    output_file = os.path.join(dir_path, "kitchen.json")
    
    if not input_file or not output_file:
        print("Error: Either provide input_file and output_file as arguments or set INPUT_FILE and OUTPUT_FILE environment variables.")
        sys.exit(1)
    counter = 0
    while counter < time_scan: 
    # while True:
        
        time.sleep(1)
        
        
        if os.path.exists(output_file) and os.path.getsize(output_file) >= MAX_FILE_SIZE:
            os.remove(output_file)

        json_data = read_json_from_file(input_file)
        if not json_data:
            continue
        append_json_to_file(output_file, json_data)
        counter += 1
            # Calculate and print progress
        progress = (counter / time_scan) * 100
        print(f'Progress: {progress:.2f}%\r', end='')

if __name__ == "__main__":
    main()
