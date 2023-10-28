import time
import serial
from datetime import datetime, timedelta
from config import TOPIC, BROKER_ADDRESS
from mqtt_setup import setup_mqtt
from cup_monitor import CupMonitor

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    monitor = CupMonitor()
    mqtt_client = setup_mqtt()

    while True:
        fsr_reading = monitor.read_sensor(ser)
        if fsr_reading is not None:
            weight = monitor.convert_to_grams(fsr_reading)
            monitor.handle_cup_placement(weight, ser)
            monitor.handle_notifications(weight, ser)

            data_payload = {
                "event_time": (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                "weight": round(weight, 2),
                "next_hydrate": monitor.state['next_notification']
            }
            mqtt_client.publish(data_payload)

        time.sleep(0.5)
