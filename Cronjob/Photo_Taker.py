import os
import subprocess
from datetime import datetime

class CameraCaptureAndFileFinder:
    def __init__(self, directory="/home/fydp-group-14/CronJob/"):
        """Initialize the class with a directory for storing images."""
        self.directory = directory
        self.command_template = "libcamera-still -n -o {}/{}.jpg"
        self.jpg_files = self.find_jpg_files()

    def capture_photo(self):
        """Generate a filename based on the current date and time, then execute the libcamera command."""
        # Get the current date and time formatted as yyyy-mm-dd_HH-MM-SS
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = self.command_template.format(self.directory, timestamp)  # Replace placeholder with timestamp

        # Execute the command using subprocess
        try:
            subprocess.run(filename, shell=True, check=True)
            print(f"Photo saved as {self.directory}{timestamp}.jpg")
            
            # After capturing the photo, refresh the list of JPG files
            self.jpg_files = self.find_jpg_files()  # Add the new photo to the list immediately
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")

    def find_jpg_files(self):
        """Scans the folder for .jpg files and stores only the file names."""
        return [file for file in os.listdir(self.directory) if file.lower().endswith(".jpg")]

    def display_jpg_files(self):
        """Displays the found JPG files."""
        if self.jpg_files:
            print("Found JPG files:")
            for file in self.jpg_files:
                print(file)
        else:
            print("No JPG files found.")

    def sort_jpg_files_by_datetime(self, output=True):
        """Sorts the JPG files by their timestamp in the filename (ascending order)."""
        # Sort the files based on the timestamp part of the filename (before .jpg)
        self.jpg_files.sort(key=lambda x: datetime.strptime(x.split('.')[0], "%Y-%m-%d_%H-%M-%S"))
        
        if output:
            print("Sorted JPG files by date and time:")
            for file in self.jpg_files:
                print(file)

# Example usage
if __name__ == "__main__":
    camera_and_finder = CameraCaptureAndFileFinder()

    # Capture a photo
    camera_and_finder.capture_photo()

    # Display and sort JPG files
    camera_and_finder.display_jpg_files()

    # Sort the files by date and time
    camera_and_finder.sort_jpg_files_by_datetime()
