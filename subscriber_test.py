import ssl
import paho.mqtt.client as mqtt

# MQTT broker details
broker_url = "3.25.58.119"
broker_port = 8883

# Path to your certificate files
ca_cert_filepath = "./certs/ca.crt"
client_cert_filepath = "./certs/server.crt"
client_key_filepath = "./certs/server.key"


# Callback function for when a message is received
def on_message(client, userdata, message):
    print("Received message on topic:", message.topic)
    print("Message payload:", message.payload.decode())


# Callback function for when the connection to the broker is established
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Connection failed with error code:", rc)
    client.subscribe("mate/hello")  # Subscribe to the desired topic here


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
