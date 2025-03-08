from Emails.Emailer import EmailSender  # Importing the class from email_sender.py
from Photo_ import JPGFileFinder



finder = JPGFileFinder()
photos = finder.find_jpg_files()

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