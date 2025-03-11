
from Chatgpt import PlantDiseaseAnalyzer
from Photo_Taker import CameraCaptureAndFileFinder



captures = CameraCaptureAndFileFinder()

#Finds all the photos 
captures.find_jpg_files()
#Captures Photos
captures.capture_photo()
#Updates List
photos =captures.jpg_files


if photos:
    print(photos)
    #Use the most recent photo
    focus = photos[0]
    

    #Run Analysis
    analyzer = PlantDiseaseAnalyzer(image_filename=focus, receiver_email = "timothymanuel295@gmail.com", email_subject="Lettuce Status")
    analyzer.run_analysis()
    