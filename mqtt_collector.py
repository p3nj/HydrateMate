import os
import csv
from hydratemate.mqtt_secure_subscriber import MQTTSecureSubscriber

directory = './data'
csv_file_path = './data/weights.csv'
last_saved_weight = None
last_saved_zero = False
weight_threshold = 20  # Weight must change by at least this amount to be saved again

def custom_on_message(client, userdata, message):
    global last_saved_weight, last_saved_zero
    try:
        decrypted_data = mqtt_subscriber.decrypt_payload(message.payload)
        mqtt_subscriber.verify_crc(decrypted_data)

        if decrypted_data:
            current_weight = decrypted_data['data']['weight']

            # Logic to handle zero and non-zero weights
            if current_weight == 0:
                if not last_saved_zero:
                    save_to_csv(decrypted_data)
                    last_saved_zero = True
            else:
                if last_saved_weight is None or abs(last_saved_weight - current_weight) >= weight_threshold:
                    save_to_csv(decrypted_data)
                    last_saved_weight = current_weight
                    last_saved_zero = False

    except Exception as e:
        print(f"An error occurred: {e}")

def save_to_csv(data):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_exists = os.path.isfile(csv_file_path)

    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)

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

