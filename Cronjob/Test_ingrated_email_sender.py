from Emails.Emailer import EmailSender  # Importing the class from email_sender.py

from Photo_Taker import CameraCaptureAndFileFinder



captures = CameraCaptureAndFileFinder()

captures.find_jpg_files()
captures.sort_jpg_files_by_datetime(output=False)
captures.capture_photo()
photos =captures.jpg_files


if photos:
    print(photos)
    # Create an instance of EmailSender
    email_sender = EmailSender()

    # Define email details
    receiver = "timothymanuel295@gmail.com"
    subject = "Test Email"
    body = "Hello, this is a test email sent using Python!"

    # Send the email
    email_sender.send_email(receiver, subject, body)