import os

class JPGFileFinder:
    def __init__(self, directory=None):
        # If no directory is provided, use the current script's directory by default
        self.directory = directory or os.path.dirname(os.path.realpath(__file__))
        self.jpg_files = self.find_jpg_files()

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

if __name__ == "__main__":
    # Create an instance of JPGFileFinder
    jpg_finder = JPGFileFinder()
    
    # Display the found JPG files
    jpg_finder.display_jpg_files()
