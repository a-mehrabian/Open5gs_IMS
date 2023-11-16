# Import necessary libraries
import os
import time
import json
import scipy
import joblib
import warnings
import threading
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score
from paho.mqtt import client as mqtt_client
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split
from mqtt import connect_mqtt, publish

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


# global real_time_data
def read_json_from_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

def start_mqtt_loop():
    client = connect_mqtt()
    client.loop_start()
    return client

# Disable the UserWarning
warnings.filterwarnings('ignore')
script_dir = os.path.dirname(os.path.realpath(__file__))
#-----------------------------------------
# @tf.function
def train_mlp_model():
    # Load the data
    data_path = os.path.join(script_dir, "data/Filter1.csv")
    data = pd.read_csv(data_path)

    # Select the features (columns) that will be used as input
    features = data[['RSRP_Serving_Cell', 'RSRQ_Serving_Cell', 'UE_Power_Headroom', 'Pusch_SNR', 'Total_BLER', 'USR_UE_Power_Headroom', 'Estimated UE power', 'SNR', 'timing offset', 'dl cqi', 'ul cqi','spatial power 1','spatial power 2','channel est ofdm 1','channel est ofdm 2','UCI low','UCI high']]

    # Labels: Room_Name is your output
    # make the labels numerical (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
    labels = data['Room_Name']


    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=88)

    # Standardize the features (important for neural networks)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Create an MLP classifier
    # mlp = MLPClassifier(hidden_layer_sizes=(100,500, 300), max_iter=10000, random_state=88)
    # mlp = MLPRegressor(hidden_layer_sizes=(100,500, 300), max_iter=10000, random_state=88)
    # Build the TensorFlow model
    mlp = tf.keras.Sequential([
        tf.keras.layers.Dense(100, activation='relu', input_shape=(X_train.shape[1],)),
        tf.keras.layers.Dense(500, activation='relu'),
        tf.keras.layers.Dense(300, activation='relu'),
        tf.keras.layers.Dense(len(pd.unique(labels)), activation='softmax')  # Assuming Room_Name is categorical
    ])

    # # Compile the model
    mlp.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])


    # Train the MLP model
    mlp.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = mlp.predict(X_test)

    # Evaluate the model
    # mse = mlp.evaluate(X_test, y_test, verbose=0)[0]
    # print("Mean Squared Error:", mse)

    # print(f'ML Accuracy: {accuracy*100:.2f} %')
    model_filename = os.path.join(script_dir, "mlp_model.h5")
    # joblib.dump(mlp, model_filename)
    mlp.save(model_filename)
    return scaler


def process_entry(entry, scaler, mqtt_client,update_time):
    # Initialize variables for collecting room name predictions
    room_name_predictions = []
    refresh_time = 1  # The time interval (in seconds) for calculating the average room name

    # Load the trained MLP model
    model_filename = os.path.join(script_dir, "mlp_model.h5")
    # mlp = joblib.load(model_filename)
    mlp = tf.keras.models.load_model(model_filename)
    all_data=[]
    rnti = list(entry.keys())[0]
    imsi = entry[rnti]['imsi']
    entry_data = {
        "RSRP_Serving_Cell": entry[rnti]['RRC_UE_REPORT']['rsrp_serving_cell'],
        "RSRQ_Serving_Cell": entry[rnti]['RRC_UE_REPORT']['rsrq_serving_cell'],
        "UE_Power_Headroom": entry[rnti]['MAC']['ue_power_headroom'],
        "Pusch_SNR": entry[rnti]['MAC']['pusch_snr'],
        "Total_BLER": entry[rnti]['MAC']['total_BLER'],
        "USR UE_Power_Headroom":entry[rnti]['MAC']['UL_SDU_RX']['ue_power_headroom'],
        "Estimated UE power":entry[rnti]['MAC']['UL_SDU_RX']['estimated_ue_power'],
        "SNR":entry[rnti]['MAC']['UE_STATs']['snr'],
        "timing offset": entry[rnti]['L1']['USHCH']['timing_offset'],
        "dl cqi":entry[rnti]['MAC']['CSI']['dl_cqi'],
        "ul cqi":entry[rnti]['MAC']['UL_SDU_RX']['ul_cqi'],
        "spatial power 1":entry[rnti]['L1']['L1Measurments']['rx_spatial_power_db'][0][0],
        "spatial power 2":entry[rnti]['L1']['L1Measurments']['rx_spatial_power_db'][1][0],
        "channel est ofdm 1":entry[rnti]['L1']['SRS']['channel_estimate_per_ofdm'][0],
        "channel est ofdm 2":entry[rnti]['L1']['SRS']['channel_estimate_per_ofdm'][1],
        "UCI low":entry[rnti]['L1']['UCI']['pucch1_low_power_stat'][0],
        "UCI high":entry[rnti]['L1']['UCI']['pucch1_high_power_stat'][0] 
    }

    # Modify the input to have the correct number of features (11)
    scaled_input = scaler.transform([[
        entry_data['RSRP_Serving_Cell'],
        entry_data['RSRQ_Serving_Cell'],
        entry_data['UE_Power_Headroom'],
        entry_data['Pusch_SNR'],
        entry_data['Total_BLER'],
        entry_data['USR UE_Power_Headroom'],
        entry_data['Estimated UE power'],
        entry_data['SNR'],
        entry_data['timing offset'],
        entry_data['dl cqi'],
        entry_data['ul cqi'],
        entry_data['spatial power 1'],
        entry_data['spatial power 2'],
        entry_data['channel est ofdm 1'],
        entry_data['channel est ofdm 2'],
        entry_data['UCI low'],
        entry_data['UCI high']
        
    ]])

    # # Convert NumPy int64 to Python int
    # scaled_input = scaled_input.astype(int)

    # Predict the room name based on the sample input data
    predicted_point = mlp.predict(scaled_input)

    # Predict the room name based on the sample input data
    room_name_predictions.append(predicted_point[0])

    # print(time.time() - update_time, refresh_time )
    # Check if 10 seconds have passed
    if time.time() - update_time >= refresh_time:
        if room_name_predictions:
            # Calculate the most common room name (mode) as the "average"
            # average_prediction = max(set(room_name_predictions), key=room_name_predictions.count)
            # print(room_name_predictions)
            average_prediction = np.argmax(room_name_predictions)
            # print(average_prediction)
            # average_prediction = max(set(tuple(prediction.all() for prediction in room_name_predictions)), key=room_name_predictions.count)

            print(f"Predicted Zone: {average_prediction}", end='\r')
        else:
            print(f"No room name predictions made in the last {refresh_time} seconds", end='\r')
        
        #cahnge the average_prediction to the room_names = ['CONFERENCE', 'WAITING', 'OFFICE','WORKSHOP','KITCHEN']
        room_names = ['CONFERENCE', 'WAITING', 'OFFICE','WORKSHOP','KITCHEN']
        average_prediction = room_names[average_prediction]
        
        # real_time_result = average_prediction
        # topic = "localization/pos/lte"  # Change to your desired topic
        tag_id = imsi
        real_time_data = { 
            tag_id: {"data": average_prediction}
        }


        # Convert the data into a JSON string
        topic = "localization/pos/lte"
        json_data = json.dumps(real_time_data, cls=NumpyEncoder)
        # json_data = json.dumps(real_time_data)
        # print(json_data)
        publish(mqtt_client, topic, json_data.encode('utf-8'))
        room_name_predictions = []  # Reset the list
        update_time = time.time()



def realtime_prediction(scaler, mqtt_client):

    # input_file = os.path.join(script_dir, "../localization_stats.log")
    input_file = os.path.join(script_dir, "../test.log")
    update_time = time.time()


    while True:
        time.sleep(1)
        json_data = read_json_from_file(input_file)
        # real_time_data_export={}
        if json_data == []:
            print("No data to process (UE not connected)")
            continue
        else:

            for entry in json_data:
                process_entry(entry, scaler, mqtt_client,update_time)



# Main function
if __name__ == '__main__':
    # Train the MLP model
    scaler = train_mlp_model()
    mqtt_client = start_mqtt_loop()
    # Start the data processing thread
    data_processing_thread = threading.Thread(target=realtime_prediction, args=(scaler, mqtt_client,))
    data_processing_thread.start()
    data_processing_thread.join()
    # print(real_time_result)