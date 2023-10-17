import json
import binascii
import ssl
import paho.mqtt.client as mqtt
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class MQTTSecureSubscriber:
    def __init__(self):
        self.client = mqtt.Client()
        #self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.private_key = None

    def setup(self, ca_certs, certfile, keyfile, topic, custom_on_message, broker_address, port=8883):
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

        if custom_on_message:
            self.client.on_message = custom_on_message
        else:
            self.client.on_message = self.default_on_message

        with open(keyfile, "rb") as key_file:
            self.private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

    def connect(self):
        self.client.connect(self.broker_address, self.port, 60)
        self.client.subscribe(self.topic)
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print("Connection failed with error code:", rc)

    def default_on_message(self, client, userdata, message):
        print("Received message on topic:", message.topic)
        decrypted_data = self.decrypt_payload(message.payload)
        self.verify_crc(decrypted_data)

    def decrypt_payload(self, payload):
        try:
            decrypted_data = self.private_key.decrypt(
                payload,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            decrypted_data_json = json.loads(decrypted_data.decode('utf-8'))
            print("Decrypted data:", decrypted_data_json)
            return decrypted_data_json
        except Exception as e:
            print(f"An error occurred while decrypting: {e}")

    def verify_crc(self, message):
        received_crc32 = message["crc"]
        crc_data = message["data"]
        calculated_crc32 = binascii.crc32(json.dumps(crc_data).encode())
        if str(calculated_crc32) == received_crc32:
            print("CRC Verification: Data is valid.")
        else:
            print("CRC Verification: Data is corrupted.")

