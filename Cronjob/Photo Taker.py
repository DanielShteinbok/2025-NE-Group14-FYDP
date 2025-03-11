import subprocess
from datetime import datetime

class CameraCapture:
    def __init__(self):
        """Initialize the class."""
        self.command_template = "libcamera-still -n -o /home/fydp-group-14/{}.jpg"
    
    def capture_photo(self):
        """Generate a filename based on the current date and time, then execute the libcamera command."""
        # Get the current date and time formatted as yyyy-mm-dd_HH-MM-SS
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = self.command_template.format(timestamp)  # Replace placeholder with timestamp

        # Execute the command using subprocess
        try:
            subprocess.run(filename, shell=True, check=True)
            print(f"Photo saved as /home/fydp-group-14/{timestamp}.jpg")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")

# Example usage
if __name__ == "__main__":
    camera = CameraCapture()
    camera.capture_photo()
