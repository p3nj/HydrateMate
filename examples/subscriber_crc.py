import binascii
import ssl
import json
import paho.mqtt.client as mqtt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# MQTT broker details
broker_url = "3.25.58.119"
broker_port = 8883

# Path to your certificate files
ca_cert_filepath = "./certs/ca.crt"
client_cert_filepath = "./certs/server.crt"
client_key_filepath = "./certs/server.key"

# Load the private key for decryption (on the server side)
with open("./certs/server.key", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )


# Callback function for when a message is received
def on_message(client, userdata, message):
    print("Received message on topic:", message.topic)
    print("Message payload:", message.payload)
    verify_crc(decrypt_payload(message.payload))

# Callback function for when the connection to the broker is established
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Connection failed with error code:", rc)
    client.subscribe("mate/data")  # Subscribe to the desired topic here
    print("Subscribed to topic.")


def decrypt_payload(payload):
    # Decrypt the data
    try:
        decrypted_data = private_key.decrypt(
            payload,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # Convert the decrypted data back to a JSON object if needed
        decrypted_data_json = json.loads(decrypted_data.decode('utf-8'))
        print("Decrypted data:", decrypted_data_json)
        # print(type(decrypted_data_json))
        return decrypted_data_json
    except Exception as e:
        print(f"An error occurred while decrypting: {e}")


def verify_crc(message):
    received_crc32 = message["crc"]
    crc_data = message["data"]
    # Calculate CRC32 of decrypted data
    calculated_crc32 = binascii.crc32(json.dumps(crc_data).encode())

    # Verify CRC32
    if str(calculated_crc32) == received_crc32:
        print("CRC Verification: Data is valid.")
    else:
        print("CRC Verification: Data is corrupted.")


# MQTT client setup
client = mqtt.Client()

# Set the callback functions
client.on_message = on_message
client.on_connect = on_connect

# Set the security options
client.tls_set(
    ca_certs="./certs/ca.crt",
    certfile="./certs/server.crt",
    keyfile="./certs/server.key",
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS #Explicitly set the TLS version (optional)
)

try:
    # Connect to the MQTT broker
    client.connect(broker_url, broker_port)
except Exception as e:
    print("MQTT connection error:", str(e))
    exit(1)

# Start the MQTT network loop
client.loop_start()

try:
    # Keep the script running to receive messages
    while True:
        pass
except KeyboardInterrupt:
    # Handle keyboard interrupt (Ctrl+C)
    print("Received keyboard interrupt. Disconnecting...")

# Disconnect from the MQTT broker
client.disconnect()

# Stop the MQTT network loop
client.loop_stop()

