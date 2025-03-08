import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, sender_email="tm5152838@gmail.com", app_password="fict tlaq ltaw rjtr", smtp_server="smtp.gmail.com", smtp_port=587):
        self.sender_email = sender_email
        self.app_password = app_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, receiver_email, subject, body):
        """Sends an email with the given subject and body."""
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

# Usage example
if __name__ == "__main__":
    sender = EmailSender()
    