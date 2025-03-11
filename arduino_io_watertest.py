import serial
import csv
import time
import threading

# Configure the serial connection (change the port accordingly)
# SERIAL_PORT = "/dev/ttyUSB0"  # Adjust for your system (e.g., "COM3" on Windows, "/dev/ttyUSB0" or "/dev/ttyACM0" on Linux)
SERIAL_PORT = "COM3"  # Adjust for your system (e.g., "COM3" on Windows, "/dev/ttyUSB0" or "/dev/ttyACM0" on Linux)
BAUD_RATE = 9600
# CSV_FILENAME = "arduino_data.csv"

# Open the serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Ensure serial connection stabilizes
time.sleep(2)
runtime = 0
status = ""

CSV_FILENAME = input("Enter the CSV filename to log data: ").strip()
if not CSV_FILENAME.endswith(".csv"):
    CSV_FILENAME += ".csv"

# Open CSV file and write the header if not exists
with open(CSV_FILENAME, "a", newline="") as file:
    writer = csv.writer(file)
    if file.tell() == 0:  # Write header only if file is empty
        writer.writerow(["Last Flow Zeroed", "Runtime", "Flow Counts", "Distance"])

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
                        last_zeroed = int(data[0].strip())
                        runtime = int(data[1].strip())
                        flow_counts = int(data[2].strip())
                        distance = float(data[3].strip())

                        # Append to CSV safely
                        with lock, open(CSV_FILENAME, "a", newline="") as file:
                            writer = csv.writer(file)
                            writer.writerow([last_zeroed, runtime, flow_counts, distance])
                            status = f"[Arduino] {runtime}, {flow_counts}, {distance}"

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