import time
import ssl
import paho.mqtt.client as mqtt


# Callback when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

# Callback when the client receives a PUBACK response from the server.
def on_publish(client, userdata, mid):
    print("Message Published.")

# Initialize MQTT client
client = mqtt.Client()
# Set TLS using the CA certificate
#client.tls_set(ca_certs="./certs/ca.crt")

# Set the security options
client.tls_set(
    ca_certs="./certs/ca.crt", 
    certfile="./certs/server.crt", 
    keyfile="./certs/server.key", 
    cert_reqs=ssl.CERT_NONE,
    tls_version=ssl.PROTOCOL_TLS, 
    ciphers=None
)

# Set the callback functions
client.on_connect = on_connect
client.on_publish = on_publish


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
