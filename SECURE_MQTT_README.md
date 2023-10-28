# MQTT Secure Python Classes

## Publisher

### Usage

```
# Initialize MQTTSecureClient mqtt_client = MQTTSecureClient()

# Setup
mqtt_client.setup(
    ca_certs="./certs/ca.crt",
    certfile="./certs/server.crt",
    keyfile="./certs/server.key",
    topic="mate/hello",
    broker_address="3.25.58.119"
)

# Connect
mqtt_client.connect()

# Data to send
data_payload = {
    "event_time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
    "weight": "100g"
}

# Publish
mqtt_client.publish(data_payload)

# Disconnect
mqtt_client.disconnect()
```

## Subscriber

## Usage

```
# Custom on_message function
def custom_on_message(client, userdata, message):
    print(f"Custom handling for message on topic {message.topic}")

# Initialize MQTTSecureSubscriber
mqtt_subscriber = MQTTSecureSubscriber()

# Setup with custom on_message function
mqtt_subscriber.setup(
    ca_certs="./certs/ca.crt",
    certfile="./certs/server.crt",
    keyfile="./certs/server.key",
    topic="mate/hello",
    broker_address="3.25.58.119",
    custom_on_message=custom_on_message  # Pass custom function here
)

# Connect
mqtt_subscriber.connect()
```
