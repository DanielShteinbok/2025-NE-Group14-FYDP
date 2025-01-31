import serial
import pandas as pd
import time

class ArduinoDataLogger:
    def __init__(self, port, baud_rate=9600, timeout=1):
        """Initialize the Arduino data logger."""
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.data = []
        self.ser = None

    def connect(self):
        """Establish a connection to the Arduino."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)  # Allow time for initialization
            print(f"Connected to {self.port} at {self.baud_rate} baud.")
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")

    def save_to_csv(self):
        """Save the collected data to a CSV file."""
        if not self.data:
            print("No data to save.")
            return

        df = pd.DataFrame(self.data, columns=['Time (s)', 'Temperature (C)', 'Temperature (F)', 'Distance (cm)', 'TDS (ppm)', 'Flow Rate (L/min)'])
        filename = f"arduino_output_{int(time.time())}.csv"
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")

    def read_data(self):
        """Read and log data from the Arduino."""
        if not self.ser:
            print("Serial connection not established.")
            return

        start_time = time.time()
        print("Reading data from Arduino. Press Ctrl+C to stop.")

        try:
            while True:
                line = self.ser.readline().decode('utf-8').strip()

                if line:
                    print(line)
                    parts = line.split('|')

                    if len(parts) == 6:
                        elapsed_time = round(time.time() - start_time, 2)

                        try:
                            temp_c = float(parts[1].strip().split(' ')[0])
                            temp_f = float(parts[2].strip().split(' ')[0])
                            distance = float(parts[3].strip().split(' ')[0])
                            tds = float(parts[4].strip().split(' ')[0])
                            flow_rate = float(parts[5].strip().split(' ')[0])

                            self.data.append([elapsed_time, temp_c, temp_f, distance, tds, flow_rate])
                        except ValueError:
                            print("Error parsing data. Skipping line.")

        except KeyboardInterrupt:
            print("\nStopping data collection.")

    def close(self):
        """Close the serial connection."""
        if self.ser:
            self.ser.close()
            print("Serial connection closed.")

# Usage example:
if __name__ == "__main__":
    logger = ArduinoDataLogger(port='COM3', baud_rate=9600)
    
    logger.connect()
    try:
        logger.read_data()
    finally:
        logger.close()
        logger.save_to_csv()
