import os
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

load_dotenv()


configuration = ConnectionConfig(

    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = 587,

    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,

     USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,

)


async def send_email(recipient:str, subject:str, body:str):
    """
    This function runs in the background after the user gets a response

    """
    

    # prepare the email
    message = MessageSchema(

            recipients = [recipient],
            subject = subject,
            body = body,
            subtype = "html"

        )
    
    fm = FastMail(config=configuration)
   

    # Try sending the mail
    try:
        print(f"sending email to {recipient}...")
        import socket

        try:
            ip = socket.gethostbyname("smtp.gmail.com")
            print("Resolved:", ip)
        except Exception as e:
            print("DNS failed:", e)

            import socket

        try:
            s = socket.create_connection(("smtp.gmail.com", 587), timeout=10)
            print("TCP connection successful")
            s.close()
        except Exception as e:
            print("TCP failed:", repr(e))
        await fm.send_message(message=message)
        print("Email sent successfully!")

    except Exception as e:
        print(f"Mail failed: {e}")

   
        