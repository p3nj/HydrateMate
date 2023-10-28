from mqtt_secure_publiher import MQTTSecureClient
from config import TOPIC, BROKER_ADDRESS

def setup_mqtt():
    mqtt_client = MQTTSecureClient()
    mqtt_client.setup(
        ca_certs="../certs/ca.crt",
        certfile="../certs/server.crt",
        keyfile="../certs/server.key",
        topic=TOPIC,
        broker_address=BROKER_ADDRESS
    )
    mqtt_client.connect()
    return mqtt_client

