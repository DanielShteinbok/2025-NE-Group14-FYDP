import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
import os

class EmailSender:
    def __init__(self, sender_email="tm5152838@gmail.com", app_password="fict tlaq ltaw rjtr", smtp_server="smtp.gmail.com", smtp_port=587):
        self.sender_email = sender_email
        self.app_password = app_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, receiver_email, subject, body, attachment_filename=None, image_filename=None):
        """
        Sends an email with the given subject, body, and optional attachments (file or image).

        :param receiver_email: Email address of the receiver.
        :param subject: Subject of the email.
        :param body: Body text of the email.
        :param attachment_filename: Path to the file to be attached (optional).
        :param image_filename: Path to the image to be attached (optional).
        """
        # Create the email message
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach a file if provided
        if attachment_filename:
            self._attach_file(msg, attachment_filename)

        # Attach an image if provided
        if image_filename:
            self._attach_image(msg, image_filename)

        # Send the email
        self._send_email_message(msg)

    def _attach_file(self, msg, filename):
        """Attaches a file to the email message."""
        try:
            filepath = os.path.join(os.getcwd(), filename)
            with open(filepath, "rb") as file:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(filename)}")
                msg.attach(part)
        except Exception as e:
            print(f"Error attaching file '{filename}': {e}")

    def _attach_image(self, msg, filename):
        """Attaches an image to the email message."""
        try:
            imagepath = os.path.join(os.getcwd(), filename)
            with open(imagepath, "rb") as image:
                image_part = MIMEImage(image.read())
                image_part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(filename)}")
                msg.attach(image_part)
        except Exception as e:
            print(f"Error attaching image '{filename}': {e}")

    def _send_email_message(self, msg):
        """Sends the email message using the SMTP server."""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

# Usage example
# email_sender = EmailSender()
# email_sender.send_email(
#     receiver_email="receiver@example.com",
#     subject="Subject",
#     body="Body text",
#     attachment_filename="document.txt",
#     image_filename="photo.jpg"
# )