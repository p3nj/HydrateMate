import os
import csv
import json
from flask import Flask, render_template
import pandas as pd
from hydratemate.mqtt_secure_subscriber import MQTTSecureSubscriber  # Import your class

app = Flask(__name__)

# Initialize MQTTSecureSubscriber
mqtt_subscriber = MQTTSecureSubscriber()

# Custom on_message function to handle incoming MQTT messages
def custom_on_message(client, userdata, message):
    # print(f"Custom handling for message on topic {message.topic}")

    # Decrypt the payload and verify CRC
    decrypted_data = mqtt_subscriber.decrypt_payload(message.payload)
    mqtt_subscriber.verify_crc(decrypted_data)

    # Check if decryption and verification were successful
    if decrypted_data:
        directory = './web'
        if not os.path.exists(directory):
           os.makedirs(directory)

        csv_file_path = './web/data.csv'
        file_exists = os.path.isfile(csv_file_path)

        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=decrypted_data.keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(decrypted_data)

# Setup MQTT with custom on_message function
mqtt_subscriber.setup(
    ca_certs="./certs/ca.crt",
    certfile="./certs/server.crt",
    keyfile="./certs/server.key",
    topic="mate/data",
    custom_on_message=custom_on_message,
    broker_address="3.25.58.119",
)

# Connect MQTT
mqtt_subscriber.connect()

@app.route('/')
def index():
    df = pd.read_csv('./web/data.csv')
    return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)  # Publicly accessible
    except KeyboardInterrupt:
        print("Received keyboard interrupt. Disconnecting...")
        mqtt_subscriber.disconnect()
 
