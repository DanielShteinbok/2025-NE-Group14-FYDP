from openai import OpenAI
import os
import base64
from Emailer import EmailSender

class PlantDiseaseAnalyzer:
    def __init__(self, image_filename, receiver_email, email_subject):
        """
        Initializes the PlantDiseaseAnalyzer class.

        :param image_filename: Name of the image file to analyze.
        :param receiver_email: Email address to send the analysis results.
        :param email_subject: Subject of the email.
        """
        self.image_filename = image_filename
        self.receiver_email = receiver_email
        self.email_subject = email_subject
        self.openai_client = OpenAI(api_key=os.getenv("openai"))  # Initialize OpenAI client

    def analyze_image(self):
        """
        Analyzes the image using OpenAI's GPT-4 model and returns the response.
        """
        image_path = os.path.join(os.getcwd(), self.image_filename)  # Get full image path

        # Read and encode the image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        # Send the image to OpenAI for analysis
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a professional botanist specialized in plant diseases."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image and provide a response with the following format: {\"score\": <likelihood of disease from 0 to 1>, \"content\": <explanation>, \"diagnosis\": <list of diagnostics>}, \"recommendations\": <list of recommendations>}"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        return response.choices[0].message.content

    def process_response(self, response):
        """
        Processes the response from OpenAI and formats it for email.

        :param response: The raw response from OpenAI.
        :return: Formatted email body if successful, None otherwise.
        """
        try:
            response_content = eval(response)  # Convert response to dictionary
            score = float(response_content.get("score", -1))
                
            

            if 0.5 <= score <= 1:
                # Format the email body
                email_body = (
                    f"Likelihood of disease: {response_content['score']}\n\n"
                    f"Explanation: {response_content['content']}\n\n"
                    f"Diagnosis: {', '.join(response_content['diagnosis']) if response_content['diagnosis'] else 'No diagnosis provided'}\n\n"
                    f"Recommendations:\n"
                )

                for recommendation in response_content['recommendations']:
                    email_body += f"- {recommendation}\n"
                

                return email_body
            else:
                print("Invalid response format: Score out of range.")
                return None

        except (ValueError, SyntaxError, KeyError) as e:
            print(f"Invalid response format: {e}")
            return None

    def send_analysis_email(self, email_body):
        """
        Sends an email with the analysis results.

        :param email_body: The formatted email body.
        """
        if email_body:
            email_sender = EmailSender()
            email_sender.send_email(self.receiver_email, self.email_subject, email_body, image_filename=self.image_filename)
        else:
            print("No email body to send.")

    def run_analysis(self):
        """
        Runs the full analysis workflow: analyze image, process response, and send email.
        """
        response = self.analyze_image()
        email_body = self.process_response(response)
        self.send_analysis_email(email_body)


if __name__ == "__main__":
    # Example usage
    analyzer = PlantDiseaseAnalyzer(image_filename="lettuce_dieased.jpg", receiver_email = "timothymanuel295@gmail.com", email_subject="Lettuce Status")
    analyzer.run_analysis()