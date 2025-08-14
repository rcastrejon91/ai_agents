import os
import smtplib
from email.mime.text import MIMEText

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_USER', 'lyra@ai.com')
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(os.getenv('EMAIL_USER', 'YOUR_EMAIL'), os.getenv('EMAIL_PASSWORD', 'YOUR_PASSWORD'))
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
