import serial
import time
from datetime import datetime
from hydratemate.mqtt_secure_publiher import MQTTSecureClient


# Configuration Constants
#SLOPE = 0.29735449735449735
SLOPE = 0.43
DEFAULT_NOTIFICATION_INTERVAL = 5 * 60  # 5 minutes
RESET_INTERVAL = 60  # 1 minute
TOPIC="mate/data",
BROKER_ADDRESS="3.25.58.119"

# State Variables
state = {
    'is_cup_placed': False,
    'notification_interval': DEFAULT_NOTIFICATION_INTERVAL,
    'notification_count': 0,
    'previous_notification_time': time.time(),
    'previous_reset_time': time.time()
}

def read_sensor(ser):
    if ser.inWaiting() > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"Debug: Received response: {response}")  # Debug message
        return int(response.split(":")[1].strip()) if "FSR Reading:" in response else None

def convert_to_grams(fsr_reading):
    grams = fsr_reading * SLOPE
    print(f"Debug: Concerted FSR reading to grams: {grams}")  # Debug message
    return grams

def reset_notification(state):
    print("Debug: Resetting notification.")  # Debug message
    state.update({
        'is_cup_placed': False,
        'notification_interval': DEFAULT_NOTIFICATION_INTERVAL,
        'notification_count': 0,
        'previous_notification_time': time.time(),
        'previous_reset_time': time.time()
    })
    print("Notification reset.")

def handle_cup_placement(weight, state):
    print(f"Debug: Handling cup placement with weight: {weight}")  # Debug message
    current_time = time.time()
    if weight > 50 and not state['is_cup_placed']:
        state['is_cup_placed'] = True
        state['previous_notification_time'] = current_time
        state['previous_reset_time'] = current_time
        print("Cup placed.")
    elif state['is_cup_placed'] and weight < 50:
        if current_time - state['previous_reset_time'] >= RESET_INTERVAL:
            print("Resetting notification due to weight being gone for a minute.")
            reset_notification(state)
        else:
            state['previous_reset_time'] = current_time
            print("Cup lifted, updating reset time.")

def handle_notifications(weight, state, ser):
    print(f"Debug: Handling notifications with weight: {weight}")  # Debug message
    current_time = time.time()
    if state['is_cup_placed'] and current_time - state['previous_notification_time'] >= state['notification_interval'] and state['notification_count'] < 10:
        print("Notifying user.")
        ser.write(b'NOTIFY_USER\n')
        state['previous_notification_time'] = current_time
        state['notification_count'] += 1
    if state['is_cup_placed'] and weight < 100:
        state['notification_interval'] += (100 - weight) * 10 * 60 / 100
        print(f"Extending notification interval. New interval: {state['notification_interval']}")

def setup_mqtt():
    mqtt_client = MQTTSecureClient()
    mqtt_client.setup(
        ca_certs="../certs/ca.crt",
        certfile="../certs/server.crt",
        keyfile="../certs/server.key",
        topic=TOPIC,
        broker_address=BROKER_ADDRESS,
    )
    mqtt_client.connect()
    return mqtt_client


if __name__ == "__main__":
    ser = serial.Serial('/dev/rfcomm0', 9600, timeout=0.1)  # Set timeout to 0.1 seconds
    print("Debug: Serial connection initialized.")  # Debug message

    print("Debug: Setting up Secure MQTT Connection...")  # Debug message
    mqtt_client = setup_mqtt();
    data_payload = {
        "event_time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        "msg": "Secured MQTT connection Established?"
    }

    print("Debug: Entering main loop.")  # Debug message
    while True:
        fsr_reading = read_sensor(ser)
        if fsr_reading is not None:
            weight_in_grams = convert_to_grams(fsr_reading)
            handle_cup_placement(weight_in_grams, state)
            handle_notifications(weight_in_grams, state, ser)
            # Data to send
            data_payload = {
                "event_time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                "weight": weight_in_grams
            }
            mqtt_client.publish(data_payload)
        time.sleep(0.05)  # Reduced sleep time to make the loop more responsive
