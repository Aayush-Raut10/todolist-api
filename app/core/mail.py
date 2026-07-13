import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")


async def send_email(recipient: str, subject: str, body: str):
    """
    Sends an email using the Resend API.
    """

    try:
        print(f"Sending email to {recipient}...")

        response = resend.Emails.send(
            {
                "from": "dolindrabahadurraut@gmail",
                "to": recipient,
                "subject": subject,
                "html": body,
            }
        )

        print("Email sent successfully!")
        print(response)

    except Exception as e:
        print(f"Email failed: {e}")