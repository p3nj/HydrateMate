import serial
import time
from datetime import datetime
from mqtt_secure_publiher import MQTTSecureClient 

TOPIC = "mate/data"
BROKER_ADDRESS = "3.25.58.119"

class CupMonitor:
    SLOPE = 0.43
    DEFAULT_NOTIFICATION_INTERVAL = 60
    RESET_INTERVAL = 60

    def __init__(self):
        self.state = {
            'is_cup_placed': False,
            'notification_interval': self.DEFAULT_NOTIFICATION_INTERVAL,
            'next_notification': time.time(),
            'previous_notification_time': time.time(),
            'last_calculate_time': time.time(),
            'last_calculated': False,
            'annoy_mode': False  
        }

    def read_sensor(self, ser):
        if ser.inWaiting() > 0:
            response = ser.readline().decode('utf-8').strip()
            return int(response.split(":")[1].strip()) if "FSR Reading:" in response else None

    def convert_to_grams(self, fsr_reading):
        return fsr_reading * self.SLOPE

    def handle_cup_placement(self, weight, ser):
        current_time = time.time()
        if weight > 50:
            if not self.state['is_cup_placed']:
                ser.write(b'CUP_PLACED\n')
            self.state['is_cup_placed'] = True
            self.state['annoy_mode'] = False  # Reset annoy mode when cup is placed
        else:
            self.state['is_cup_placed'] = False


def handle_notifications(weight, state, ser):
    current_time = time.time()

    if state['is_cup_placed']:
        if not state['annoy_mode']:
            state['last_calculated'] = False
            state['next_notification'] = state['notification_interval'] - (current_time - state['last_calculate_time'])
            if time_remaining <= 0: time_remaining = 0
            if time_remaining == 0:
                print("Notifying user.")
                ser.write(b'NOTIFY_USER\n')
                state['previous_notification_time'] = current_time
                state['annoy_mode'] = True  # Activate annoy mode
            print(f"Debug: Handling notifications with weight: {weight}. Time remaining until next notification: {time_remaining:.2f} seconds.")
        else:
            print(f"Debug: Handling notifications with weight: {weight}. Annoy mode activated.")
    else:
        if not state['last_calculated']:
            state['last_calculate_time'] = current_time
            state['last_calculated'] = True
        state['annoy_mode'] = False  # Deactivate annoy mode when cup is lifted
        print(f"Debug: Handling notifications with weight: {weight}. Timer is paused.")

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

if __name__ == "__main__":
    ser = serial.Serial('/dev/rfcomm0', 9600, timeout=1)
    #ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    monitor = CupMonitor()
    mqtt_client = setup_mqtt()

    while True:
        fsr_reading = monitor.read_sensor(ser)
        if fsr_reading is not None:
            weight = monitor.convert_to_grams(fsr_reading)
            monitor.handle_cup_placement(weight, ser)
            handle_notifications(weight, monitor.state, ser)

            #if monitor.state['is_cup_placed']:
            #    cup_duration = time.time() - monitor.state['cup_placement_time']
            #else:
            #    cup_duration = 0

            data_payload = {
                "event_time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                "weight": round(weight, 2),
                "next_hydrate": state['
            #    "cup_duration": round(cup_duration, 2)
            }
            mqtt_client.publish(data_payload)

        time.sleep(0.5)
