import numpy as np
import serial
import csv
import time
import threading
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Function to save X and P to a file
def save_state(x, P):
    state = {
        'X': x,
        'P': P
    }
    with open('state.json', 'w') as f:
        json.dump(state, f)

# Function to load X and P from a file
def load_state():
    try:
        with open('state.json', 'r') as f:
            state = json.load(f)
            return state['X'], state['P']
    except FileNotFoundError:
        return [0, 0], [[0, 0], [0, 0]]

def kalman_update(x, P, z, dt, w, Q, R):
    # Define F matrix
    F = np.array([[1, dt],
                  [0, 1]])
    
    # Compute a priori estimate
    x_priori = np.array([x[0] + x[1] * dt + w * dt,
                          x[1]])
    
    # Compute a priori P matrix
    P_priori = F @ P @ F.T + Q
    
    # Compute innovation covariance
    S = P_priori + R
    
    # Compute inverse of S
    S_inv = np.linalg.inv(S)
    
    # Compute Kalman gain
    K = P_priori @ S_inv
    
    # Compute posterior x
    x = x_priori + K @ (z - x_priori)
    
    # Compute posterior P
    P = P_priori - K @ P_priori
    
    return x, P

# Configure the serial connection (change the port accordingly)
SERIAL_PORT = "/dev/ttyUSB0"  # Adjust for your system (e.g., "COM3" on Windows, "/dev/ttyUSB0" or "/dev/ttyACM0" on Linux)
# SERIAL_PORT = "COM3"  # Adjust for your system (e.g., "COM3" on Windows, "/dev/ttyUSB0" or "/dev/ttyACM0" on Linux)
BAUD_RATE = 9600
# CSV_FILENAME = "arduino_data.csv"

# Open the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Ensure serial connection stabilizes
time.sleep(2)
runtime = 0
status = ""

# CSV_FILENAME = input("Enter the CSV filename to log data: ").strip()
# if not CSV_FILENAME.endswith(".csv"):
#     CSV_FILENAME += ".csv"

# # Open CSV file and write the header if not exists
# with open(CSV_FILENAME, "a", newline="") as file:
#     writer = csv.writer(file)
#     if file.tell() == 0:  # Write header only if file is empty
#         writer.writerow(["Last Flow Zeroed", "Runtime", "Flow Counts", "Distance"])

# Create a new file called variables_lock.sh
with open("variables_lock.sh", "w") as file:
    file.write("#!/bin/bash\n")

# Read environment variables
import os
x, P = load_state()
Q = os.getenv('Q', '0,0').split(',')
Q = [float(i) for i in Q]
# Q = np.diag([float(i) for i in Q])
R = os.getenv('R', '0,0').split(',')
R = [float(i) for i in R]
# R = np.diag([float(i) for i in R])
w = float(os.getenv('W', '0'))

# Lock for thread safety
lock = threading.Lock()

def read_serial():
    """ Continuously read from serial, log data to CSV, and display it. """
    global runtime
    global status
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8").strip()
                data = line.split(",")

                if len(data) == 4:
                    try:
                        dt = int(data[0].strip())
                        flowcount1 = int(data[1].strip())
                        flowcount2 = int(data[2].strip())
                        distance = float(data[3].strip())
                        temperature = float(data[4].strip())
                        tdsvalue = float(data[5].strip())

                        # Kalman update
                        z = np.array([-0.787714755*distance + 9.955578414, (flowcount1 + flowcount2)*5.35391e-5/dt])
                        Q_here = Q if (flowcount1 + flowcount2) > 0 else [Q[0], 0]
                        x, P = kalman_update(x, P, z, dt, w, np.diag(Q), np.diag(R))

                        # Append to CSV safely
                        # with lock, open(CSV_FILENAME, "a", newline="") as file:
                        #     writer = csv.writer(file)
                        #     writer.writerow([last_zeroed, runtime, flow_counts, distance])
                        #     status = f"[Arduino] {runtime}, {flow_counts}, {distance}"

                        # Write temperature and tds_value as environment variables
                        os.environ['TEMPERATURE'] = str(temperature)
                        os.environ['TDS_VALUE'] = str(tdsvalue)

                        # Export environment variables to be seen by the user and other programs
                        with open("variables_lock.sh", "a") as file:
                            file.write(f"export TEMPERATURE={temperature}\n")
                            file.write(f"export TDS_VALUE={tdsvalue}\n")

                        # Rename variables_lock.sh to variables.sh
                        os.replace("variables_lock.sh", "variables.sh")

                        # Save state
                        save_state(x, P)

                        status = f"volume: {x[0]}, flowrate: {x[1]}, tds: {tdsvalue}, temperature: {temperature}"

                        # print(f"[Arduino] {runtime}, {flow_counts}, {distance}")
                    except ValueError:
                        print(f"[Warning] Skipping invalid data: {line}")

    except KeyboardInterrupt:
        print("Stopping serial read thread.")

def write_serial():
    """ Continuously wait for user input and send it to the Arduino. """
    global runtime
    global status
    try:
        pumping = False
        while True:
            command = input("Enter command to send (or type 'exit' to quit, or 'time' for time): ").strip()
            if command.lower() == "exit":
                print("Exiting program...")
                ser.close()
                break
            with lock:
                if command.lower() == "time":
                    print("runtime: ", runtime) 
                elif command.lower() == "status":
                    print(status)
                # else:
                elif command.lower() == "p" or command.lower() == "pump":
                    # ser.write((command + "\n").encode("utf-8"))  # Send command over serial
                    # print(f"[Sent] {command}")
                    to_send = "STOP PUMPING" if pumping else "START PUMPING"
                    pumping = not pumping
                    ser.write((to_send + "\n").encode("utf-8"))  # Send command over serial
                    print(f"[Sent] {to_send}")
                # elif command.lower() == "h" or command.lower() == "heat":
                elif command.split(" ")[0].lower() == "heat":
                    to_send = "HEAT "+ command.split()[1]
                    # ser.write((command + "\n").encode("utf-8"))
                    ser.write((to_send + "\n").encode("utf-8"))  # Send command over serial
                else:
                    ser.write(("STOP HEATING" + "\n").encode("utf-8"))

    except KeyboardInterrupt:
        print("Stopping user input thread.")

# Start both threads
read_thread = threading.Thread(target=read_serial, daemon=True)
write_thread = threading.Thread(target=write_serial, daemon=True)

read_thread.start()
write_thread.start()

# Wait for the write thread to complete (read thread runs indefinitely)
write_thread.join()