import time
import paho.mqtt.client as mqtt
import ssl

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
    # Publish the message
    result = client.publish("mate/hello", "It's time to hydrate! mate!")

    # Check if the publish was successful
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print("Message published successfully.")
    else:
        print("Failed to publish message.")

    # Wait for 3 seconds before the next publish
    time.sleep(3)

# Stop the loop (this line will not be reached in this example)
client.loop_stop()

# Disconnect from the broker (this line will not be reached in this example)
client.disconnect()

