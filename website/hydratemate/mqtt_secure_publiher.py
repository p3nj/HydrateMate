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

class MQTTSecureClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_log = self.on_log
        self.topic = None
        self.public_key = None

    def setup(self, ca_certs, certfile, keyfile, topic, broker_address, port=8883):
        self.client.tls_set(
            ca_certs=ca_certs,
            certfile=certfile,
            keyfile=keyfile,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS
        )
        self.broker_address = broker_address
        self.port = port
        self.topic = topic
        print(f"Debug: Topic set as {self.topic}, type: {type(self.topic)}")


        with open(certfile, "rb") as cert_file:
            cert_data = cert_file.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            self.public_key = cert.public_key()

    def connect(self):
        self.client.connect(self.broker_address, self.port, 60)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def on_publish(self, client, userdata, mid):
        print("Message Published.")

    def on_log(self, client, userdata, level, buf):
        print(f"Log: {buf}")

    def encrypt_data(self, message_json_str):
        encrypted_data = self.public_key.encrypt(
            message_json_str,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted_data

    def publish(self, data):
        event_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        crc32_hash = binascii.crc32(json.dumps(data).encode('utf-8'))
        crc32_str = str(crc32_hash)

        message_object = {
            "data": data,
            "crc": crc32_str
        }
        
        message_json_str = json.dumps(message_object).encode('utf-8')
        encrypted_data = self.encrypt_data(message_json_str)
        
        result = self.client.publish(self.topic, encrypted_data)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print("Message published successfully.")
        else:
            print("Failed to publish message.")

