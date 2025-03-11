from picamera2 import Picamera2
from time import sleep
from datetime import datetime
from PIL import Image

# Initialize the camera
picam2 = Picamera2()

# Configure the camera for still image capture
picam2.configure(picam2.create_still_configuration())

# Start the camera preview (optional, useful for testing)
picam2.start_preview()

# Wait for a moment to allow the camera to adjust
sleep(2)

# Capture the photo
image = picam2.capture_array()

# Get the current time and date as a string
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Save the image with the timestamp as the filename
im = Image.fromarray(image)
filename = f"{timestamp}.jpg"
im.save(filename)

# Stop the preview (optional)
picam2.stop_preview()

print(f"Photo saved as {filename}")
