# mqtt_collector.py

import csv
from hydratemate.mqtt_secure_subscriber import MQTTSecureSubscriber  

# Initialize MQTTSecureSubscriber
mqtt_subscriber = MQTTSecureSubscriber()

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


# Custom on_message function to handle incoming MQTT messages
def custom_on_message(client, userdata, message):
    # print(f"Custom handling for message on topic {message.topic}")

    # Decrypt the payload and verify CRC
    decrypted_data = mqtt_subscriber.decrypt_payload(message.payload)
    mqtt_subscriber.verify_crc(decrypted_data)

    # Check if decryption and verification were successful
    if decrypted_data:
        directory = './data'
        if not os.path.exists(directory):
           os.makedirs(directory)

        csv_file_path = './data/weights.csv'
        file_exists = os.path.isfile(csv_file_path)

        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=decrypted_data.keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(decrypted_data)
