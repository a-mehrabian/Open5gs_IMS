from paho.mqtt import client as mqtt_client
import time
 
# broker = '192.168.21.10' # change this to your broker's address
broker = '127.0.0.1'
port = 1883 # change this to your broker's port
client_id = 'client_id' # change this to your client id
username = 'username' # change this to your username
password = 'password' # change this to your password
 
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
 
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
 

def publish(client, topic, message):
    qos = 0  # Change this to your desired QoS level
    retain = False  # Change this to True if you want to retain the message
    result = client.publish(topic, message, qos, retain)
    status = result[0]
    if status == 0:
        print(f"Sent `{message}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

 
 
def subscribe(client):
    topic = "localization/pos/lte" # change this to your topic
    qos = 0 # change this to your desired QoS level
    client.subscribe(topic, qos)
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
 
    client.on_message = on_message
 
 
def run():
    client = connect_mqtt()
    client.loop_start()
    subscribe(client)
    publish(client)
    time.sleep(10) # change this to your desired duration
    client.loop_stop()