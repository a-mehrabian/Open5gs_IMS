import json
import os
import csv

#room_names = ['CONFERENCE', 'WAITING', 'OFFICE','WORKSHOP','KITCHEN']
room_names = ['CONFERENCE', 'WAITING','WORKSHOP','KITCHEN']

file_paths = [os.path.join(os.path.dirname(__file__), f'../fingerprint/{room_name}.json') for room_name in room_names]

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
            data_entry = [i, rnti, rsrp_serving_cell, rsrq_serving_cell, UE_Power_Headroom, Pusch_SNR, Total_BLER, USR_UE_Power_Headroom, Estimated_UE_power, SNR, timing_offset, dl_cqi, ul_cqi,spatial_power_1,spatial_power_2,channel_est_ofdm_1,channel_est_ofdm_2,UCI_low,UCI_high]

            # Append the data entry to the list of data entries
            data_entries.append(data_entry)
i=+1

# Write the data to a CSV file
exportfile = os.path.join(os.path.dirname(__file__), 'Filter.csv')
with open(exportfile, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data_entries)
