from Chatgpt import PlantDiseaseAnalyzer
from Photo_Taker import CameraCaptureAndFileFinder

captures = CameraCaptureAndFileFinder()

# Finds all the photos
captures.find_jpg_files()

# Captures Photos
captures.capture_photo()

# Sorts JPG files by number
captures.sort_jpg_files_by_number()

# Updates List
photos = captures.jpg_files

if photos:
    print(photos)
    # Use the most recent photo
    focus = "/home/fydp-group-14/CronJob/" + photos[-1]
    
    # Run Analysis
    analyzer = PlantDiseaseAnalyzer(image_filename=focus, receiver_email="timothymanuel295@gmail.com, sean.hua999@gmail.com, mostafahajjshehadeh@gmail.com, dshteinbok@gmail.com", email_subject="Lettuce Status")
    analyzer.run_analysis()
