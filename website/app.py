from flask import Flask, render_template, jsonify
import pandas as pd
import os
from hydratemate.mqtt_secure_subscriber import MQTTSecureSubscriber
import json

app = Flask(__name__)

live_data = {}

# Custom on_message function to update live_data
def custom_on_message(client, userdata, message):
    global live_data
    print(f"Received: {message.payload}")
    decrypted_data = mqtt_subscriber.decrypt_payload(message.payload)
    mqtt_subscriber.verify_crc(decrypted_data)
    if decrypted_data:
        live_data = decrypted_data

mqtt_subscriber = MQTTSecureSubscriber()
mqtt_subscriber.setup(
    ca_certs="./certs/ca.crt",
    certfile="./certs/server.crt",
    keyfile="./certs/server.key",
    topic="mate/data",
    broker_address="3.25.58.119",
    # broker_address="127.0.0.1",
    custom_on_message=custom_on_message
)

mqtt_subscriber.connect()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live_data')
def get_live_data():
    return jsonify(live_data)

@app.route('/stored_data')
def stored_data():
    if os.path.exists('./data/weights.csv'):
        df = pd.read_csv('./data/weights.csv')
        return render_template('stored_data.html', tables=[df.to_html(classes='data', index=False)], titles=df.columns.values)
    else:
        return "No data available"

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")

