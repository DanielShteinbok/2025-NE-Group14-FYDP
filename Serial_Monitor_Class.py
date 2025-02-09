import serial
import time

class ArduinoDataLogger:
    def __init__(self, port, baud_rate=9600, timeout=1):
        """Initialize the Arduino data logger."""
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None
        self.filename = f"arduino_output_{int(time.time())}.txt"

    def connect(self):
        """Establish a connection to the Arduino."""
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)  # Allow time for initialization
            print(f"Connected to {self.port} at {self.baud_rate} baud.")
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")

    def save_to_txt(self, entry):
        """Append a single data entry to the text file."""
        with open(self.filename, 'a') as file:
            file.write("\t".join(map(str, entry)) + "\n")

    def read_data(self):
        """Read and log data from the Arduino."""
        if not self.ser:
            print("Serial connection not established.")
            return

        start_time = time.time()
        print("Reading data from Arduino. Press Ctrl+C to stop.")

        # Write the header to the file only once
        with open(self.filename, 'w') as file:
            file.write("Time (s)\tTemperature (C)\tTemperature (F)\tDistance (cm)\tTDS (ppm)\tFlow Rate (L/min)\n")

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

                            entry = [elapsed_time, temp_c, temp_f, distance, tds, flow_rate]
                            
                            # Save only the latest entry instead of appending all data
                            self.save_to_txt(entry)

                        except ValueError:
                            print("Error parsing data. Skipping line.")

        except KeyboardInterrupt:
            print("\nStopping data collection.")

    def close(self):
        """Close the serial connection."""
        if self.ser:
            self.ser.close()
            print("Serial connection closed.")

    # Function to send pump duration
    def send_pump_duration(self, duration):
        print(f"Sending {duration} ms to Arduino...")
        self.ser.write(f"{duration}\n".encode())  # Send number as a string
        time.sleep(0.5)  # Give Arduino time to process

        # Read response from Arduino
        response = self.ser.readline().decode().strip()
        if response:
            print("Arduino:", response)

# Usage example:
if __name__ == "__main__":
    logger = ArduinoDataLogger(port='COM3', baud_rate=9600)
    
    logger.connect()
    
    logger.read_data()
    
