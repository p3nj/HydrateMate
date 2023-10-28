import time

class CupMonitor:
    # Weight calculation
    SLOPE = 0.43
    # Default Hydrate Time
    DEFAULT_NOTIFICATION_INTERVAL = 10

    def __init__(self):
        self.state = {
            'is_cup_placed': False,
            'notification_interval': self.DEFAULT_NOTIFICATION_INTERVAL,
            'when_cup_placed': 0.0,
            'next_notification': time.time(),
            'last_calculate_time': 0.0,
            'annoy_mode': False  
        }

    def read_sensor(self, ser):
        try:
            if ser.inWaiting() > 0:
                response = ser.readline().decode('utf-8').strip()
                return int(response.split(":")[1].strip())
        except Exception as e:
            print(f"Error reading sensor: {e}")
            return None

    # NOT WORKING.
    # However still using this value for rest of the program.
    def convert_to_grams(self, fsr_reading):
        return fsr_reading * self.SLOPE

    def handle_cup_placement(self, weight, ser):
        current_time = time.time()
        gap_threshold = 30  # Replace with your value for x seconds

        if weight > 200:
            if not self.state['is_cup_placed']:
                # Check if the gap between cup placements is greater than the threshold
                if (current_time - self.state.get('last_cup_lifted', current_time)) > gap_threshold:
                    self.state['notification_interval'] = self.DEFAULT_NOTIFICATION_INTERVAL  # Reset to default
                    ser.write(b'CUP_PLACED\n') # Buzz for user

                self.state['when_cup_placed'] = current_time  # Record when the cup is placed

            self.state['is_cup_placed'] = True
            self.state['annoy_mode'] = False

        else:
            if self.state['is_cup_placed']:
                cup_placed_duration = current_time - self.state['when_cup_placed']  # Calculate duration for which cup was placed
                self.state['notification_interval'] += cup_placed_duration  # Adjust next notification time

            self.state['is_cup_placed'] = False
            self.state['last_cup_lifted'] = current_time  # Record when the cup was last lifted


    # Handle the notification
    def handle_notifications(self, weight, ser):
        current_time = time.time()

        if self.state['is_cup_placed']:
            if not self.state['annoy_mode']:
                self.state['next_notification'] = self.state['notification_interval'] - (current_time - self.state['last_calculate_time'])

                # Milliseconds correction.
                if self.state['next_notification'] <= 0:
                    self.state['next_notification'] = 0

                if self.state['next_notification'] == 0:
                    print("Notifying user.")
                    ser.write(b'NOTIFY_USER\n')
                    self.state['annoy_mode'] = True  # Activate annoy mode

                print(f"Debug: Handling notifications with weight: {weight}. Time remaining until next notification: {self.state['next_notification']:.2f} seconds.")
                
                # Only reset last_calculate_time if annoy_mode is not active
                if not self.state['annoy_mode']:
                    self.state['last_calculate_time'] = current_time
            else:
                print(f"Debug: Annoy mode activated. No further notifications will be sent.")
        else:
            self.state['last_calculate_time'] = current_time  # Reset last_calculate_time when cup is lifted
            self.state['annoy_mode'] = False  # Deactivate annoy mode when cup is lifted
            print(f"Debug: Handling notifications with weight: {weight}. Timer is paused.")

