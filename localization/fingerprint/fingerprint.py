import sys
import os
import json
import time
import csv

#time_scan = int(input("Enter the duration in seconds for scanning: ")) # sec
time_scan = 50
dir_path = os.path.dirname(os.path.realpath(__file__))
MAX_FILE_SIZE = 2 * (1024 ** 3)  # 2GB
location_names=[]
location_ids=[]
index_locations={}

def generate_text_to_number_mapping(strings):
    text_to_number = {}
    for index, text in enumerate(strings, start=1):
        text_to_number[text.upper()] = index
    return text_to_number

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
    input_file = os.path.join(dir_path, "../../localization_stats.log")
    nof_locations = input("Enter number of locations to do fingerprint: ")
    max_file_size = MAX_FILE_SIZE
    location_names =[]
    
    for i in range(int(nof_locations)):
        location_name = input("Enter the location to do fingerprint: ").strip().upper()
        if location_name == 'DONE':
            break
        if len(location_name) == 0:
            print("Exiting.")
            break
        index_locations = generate_text_to_number_mapping(location_name)
        

        location_names.append(location_name)
        location_ids.append(i)
        output_file=location_name+'.json'
        
        
        if not input_file or not output_file or max_file_size <= 0:
            print("Error: Please provide valid input for file locations and size.")
            sys.exit(1)
            
        counter = 0
        while counter < time_scan: 
            time.sleep(1)
            
            if os.path.exists(output_file) and os.path.getsize(output_file) >= max_file_size:
                os.remove(output_file)

            json_data = read_json_from_file(input_file)
            if not json_data:
                continue
            append_json_to_file(output_file, json_data)
            counter += 1
            
            # Calculate and print progress
            progress = (counter / time_scan) * 100
            print(f'Progress: {progress:.2f}%\r', end='')

def filter_data():
    #room_names = ['CONFERENCE', 'WAITING', 'OFFICE','WORKSHOP','KITCHEN']
    #room_names = ['CONFERENCE', 'WAITING','WORKSHOP','KITCHEN']
    room_names=location_names
    file_paths = [os.path.join(os.path.dirname(__file__), f'{room_name}.json') for room_name in room_names]

    # Define the header for the CSV file
    header = ['Room_Name', 'UE_RNTI', 'RSRP_Serving_Cell', 'RSRQ_Serving_Cell', 'UE_Power_Headroom', 'Pusch_SNR', 'Total_BLER', 'USR_UE_Power_Headroom', 'Estimated UE power', 'SNR', 'timing offset', 'dl cqi', 'ul cqi','spatial power 1','spatial power 2','channel est ofdm 1','channel est ofdm 2','UCI low','UCI high']

    # Create a list to store all data entries
    data_entries = []

    for file_path in file_paths:
        i=0

        with open(file_path, 'r') as file:
            json_data = file.read()

        data = json.loads(json_data)

        room_name = file_path.split('/')[-1].split('.')[0]

        for entry_list in data:
            for entry in entry_list:
                rnti = list(entry.keys())[0]
                rsrp_serving_cell = entry[rnti]['RRC_UE_REPORT']['rsrp_serving_cell']
                rsrq_serving_cell = entry[rnti]['RRC_UE_REPORT']['rsrq_serving_cell']
                UE_Power_Headroom = entry[rnti]['MAC']['ue_power_headroom']
                Pusch_SNR = entry[rnti]['MAC']['pusch_snr']
                Total_BLER = entry[rnti]['MAC']['total_BLER']
                USR_UE_Power_Headroom = entry[rnti]['MAC']['UL_SDU_RX']['ue_power_headroom']
                Estimated_UE_power = entry[rnti]['MAC']['UL_SDU_RX']['estimated_ue_power']
                SNR = entry[rnti]['MAC']['UE_STATs']['snr']
                timing_offset = entry[rnti]['L1']['USHCH']['timing_offset']
                dl_cqi = entry[rnti]['MAC']['CSI']['dl_cqi']
                ul_cqi = entry[rnti]['MAC']['UL_SDU_RX']['ul_cqi']
                spatial_power_1=entry[rnti]['L1']['L1Measurments']['rx_spatial_power_db'][0][0]
                spatial_power_2=entry[rnti]['L1']['L1Measurments']['rx_spatial_power_db'][1][0]
                channel_est_ofdm_1=entry[rnti]['L1']['SRS']['channel_estimate_per_ofdm'][0]
                channel_est_ofdm_2=entry[rnti]['L1']['SRS']['channel_estimate_per_ofdm'][1]
                UCI_low = entry[rnti]['L1']['UCI']['pucch1_low_power_stat'][0]
                UCI_high = entry[rnti]['L1']['UCI']['pucch1_high_power_stat'][0]

                # Create a data entry list for each iteration
                data_entry = [index_locations[location_names[i]], rnti, rsrp_serving_cell, rsrq_serving_cell, UE_Power_Headroom, Pusch_SNR, Total_BLER, USR_UE_Power_Headroom, Estimated_UE_power, SNR, timing_offset, dl_cqi, ul_cqi,spatial_power_1,spatial_power_2,channel_est_ofdm_1,channel_est_ofdm_2,UCI_low,UCI_high]

                # Append the data entry to the list of data entries
                data_entries.append(data_entry)
    i=+1

    # Write the data to a CSV file
    #exportfile = os.path.join(os.path.dirname(__file__), '../data/Filter.csv')
    #exportfile =  '../data/Filter.csv'
    folder_data_path = os.path.join(os.path.dirname(__file__), '../data')  
    print(folder_data_path)
    # Set the file path in folder B for Filter.csv
    exportfile = os.path.join(folder_data_path, 'Filter.csv')
    with open(exportfile, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data_entries)
if __name__ == "__main__":
    main()
    filter_data()
   
    
    