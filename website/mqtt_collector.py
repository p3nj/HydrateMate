import os
import csv
from hydratemate.mqtt_secure_subscriber import MQTTSecureSubscriber  

directory = './data'
csv_file_path = './data/weights.csv'

def custom_on_message(client, userdata, message):
    try:
        # Your existing code for handling messages
        decrypted_data = mqtt_subscriber.decrypt_payload(message.payload)
        mqtt_subscriber.verify_crc(decrypted_data)

        if decrypted_data:
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_exists = os.path.isfile(csv_file_path)

            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=decrypted_data.keys())

                if not file_exists:
                    writer.writeheader()

                writer.writerow(decrypted_data)

    except Exception as e:
        print(f"An error occurred: {e}")

mqtt_subscriber = MQTTSecureSubscriber()

mqtt_subscriber.setup(
    ca_certs="./certs/ca.crt",
    certfile="./certs/server.crt",
    keyfile="./certs/server.key",
    topic="mate/data",
    broker_address="3.25.58.119",
    custom_on_message=custom_on_message
)

print("Connecting to MQTT...")
mqtt_subscriber.connect()
print("Connected!")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Disconnecting...")
    mqtt_subscriber.disconnect()

