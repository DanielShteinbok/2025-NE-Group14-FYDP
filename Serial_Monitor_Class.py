import serial
import pandas as pd
import time

# Specify the serial port and baud rate
PORT = 'COM3'  # Replace with your port (e.g., 'COM3', '/dev/ttyUSB0')
BAUD_RATE = 9600

# Open the serial connection
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Allow time for the connection to initialize

# List to store data
data = []

def save_to_csv(data):
    """Save the collected data to a CSV file."""
    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=['Time (s)', 'Temperature (C)', 'Temperature (F)', 'Distance (cm)', 'TDS (ppm)', 'Flow Rate (L/min)'])
    
    # Save the DataFrame to a CSV file
    filename = f"arduino_output_{int(time.time())}.csv"
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

try:
    print("Reading data from Arduino. Type 'SAVE' in the console to save to CSV.")
    start_time = time.time()

    while True:
        # Read a line from the serial monitor
        line = ser.readline().decode('utf-8').strip()

        if line:
            print(line)

            # Parse the line into components (assuming '|' as the delimiter in Arduino output)
            parts = line.split('|')
            
            # Check if data has the expected number of parts
            if len(parts) == 6:
                elapsed_time = round(time.time() - start_time, 2)

                # Parse and store the data
                try:
                    temp_c = float(parts[1].strip().split(' ')[0])
                    temp_f = float(parts[2].strip().split(' ')[0])
                    distance = float(parts[3].strip().split(' ')[0])
                    tds = float(parts[4].strip().split(' ')[0])
                    flow_rate = float(parts[5].strip().split(' ')[0])

                    # Append to data list
                    data.append([elapsed_time, temp_c, temp_f, distance, tds, flow_rate])
                except ValueError:
                    print("Error parsing data. Skipping line.")

        # Check for user input
    

except KeyboardInterrupt:
    print("\nExiting...")
    ser.close()
    
    # Prompt to save data if any exists
    if data:
        save_to_csv(data)
    else:
        print("No data to save.")

ser.close()
