import time
from Chatgpt import PlantDiseaseAnalyzer
from Photo_Taker import CameraCaptureAndFileFinder

# Initialize CameraCaptureAndFileFinder
captures = CameraCaptureAndFileFinder()

# Start tracking execution time
def log_time(task_name, start_time):
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"{task_name} took {elapsed:.2f} seconds")
    return elapsed

# Track total execution time
total_start_time = time.time()

total_time = 0

# Finds all the photos
start_time = time.time()
captures.find_jpg_files()
total_time += log_time("Finding JPG files", start_time)

# Captures Photos
start_time = time.time()
captures.capture_photo()
total_time += log_time("Capturing photo", start_time)

# Sorts JPG files by number
start_time = time.time()
captures.sort_jpg_files_by_number()
total_time += log_time("Sorting JPG files", start_time)

# Updates List
start_time = time.time()
photos = captures.jpg_files
total_time += log_time("Updating photo list", start_time)

if photos:
    print(photos)
    # Use the most recent photo
    focus = "/home/fydp-group-14/CronJob/" + photos[-1]
    
    # Run Analysis
    start_time = time.time()
    analyzer = PlantDiseaseAnalyzer(image_filename=focus, receiver_email="timothymanuel295@gmail.com, sean.hua999@gmail.com, mostafahajjshehadeh@gmail.com, dshteinbok@gmail.com", email_subject="Lettuce Status")
    analyzer.run_analysis()
    total_time += log_time("Running analysis", start_time)

total_elapsed = time.time() - total_start_time
print(f"Total execution time: {total_elapsed:.2f} seconds")
