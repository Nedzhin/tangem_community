import smtplib
from email.mime.text import MIMEText
import os 
body = "Hi brother How are you?"



async def send_email(body, username):
    subject = "Email Subject"
    sender = "nurseiit.bakkali@nu.edu.kz"
    recipients = ["nurseiitbakkali@gmail.com"]
    password = os.getenv('EMAIL_APP_KEY')

    msg = MIMEText("Query from the user:\n\n" + body + f"\n\nemail is sent by @{username}")
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")


#send_email(body, "Nurseiit")