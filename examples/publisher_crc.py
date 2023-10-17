import time
import paho.mqtt.client as mqtt
import ssl
import binascii
import json
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

# Load the X.509 certificate to get the public key
with open("./certs/server.crt", "rb") as cert_file:
    cert_data = cert_file.read()
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())

# Extract the public key from the certificate
public_key = cert.public_key()

# Callback when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

# Callback when the client receives a PUBACK response from the server.
def on_publish(client, userdata, mid):
    print("Message Published.")

# Callback for logging
def on_log(client, userdata, level, buf):
    print(f"Log: {buf}")

# Initialize MQTT client
client = mqtt.Client()

# Set the callback functions
client.on_connect = on_connect
client.on_publish = on_publish
client.on_log = on_log  # Set the on_log callback for debugging

# Set the security options
client.tls_set(
    ca_certs="./certs/ca.crt",
    certfile="./certs/server.crt",
    keyfile="./certs/server.key",
    cert_reqs=ssl.CERT_REQUIRED,
    tls_version=ssl.PROTOCOL_TLS  # Explicitly set the TLS version (optional)
)

# Connect to the broker
client.connect("3.25.58.119", 8883, 60)

# Loop forever to process network events
client.loop_start()

while True:
    # Get the current event time
    event_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    # Your data payload
    data = {
        "event_time": event_time,
        "weight": "str"
    }

    # Calculate the CRC32 hash of the data JSON string
    crc32_hash = binascii.crc32(json.dumps(data).encode('utf-8'))
    crc32_str = str(crc32_hash)

    # Create the JSON object with event_time, data, and crc
    message_object = {
        "data": data,
        "crc": crc32_str
    }

    # Convert the data to a JSON-formatted string and then to bytes
    message_json_str = json.dumps(message_object).encode('utf-8')

    # Encrypt the data using the public key
    encrypted_data = public_key.encrypt(
        message_json_str,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # Publish the JSON-formatted message
    result = client.publish("mate/data", encrypted_data)

    # Check if the publish was successful
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Message published successfully.")
    else:
        print("Failed to publish message.")

    # Wait for 1 seconds before the next publish
    time.sleep(1)
