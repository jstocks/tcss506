import os
import smtplib
from email.message import EmailMessage


def send_mail(subscriber_email):
    EMAIL_ADDRESS = os.environ.get('EMAIL_ID')
    EMAIl_PASSWORD = os.environ.get('EMAIL_PASS')
    print(EMAIL_ADDRESS)
    # subscriber_list = ["sribadevelopment@gmail.com", "sribarajendran@gmail.com"]

    msg = EmailMessage()
    msg['Subject'] = "TEST:email functionality"
    msg['From'] = EMAIL_ADDRESS
    # msg['To'] = ", ".join(subscriber_list)
    msg['To'] = subscriber_email
    msg.set_content('This is a test email from the FDA recall app')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIl_PASSWORD)
        smtp.send_message(msg)


if __name__ == "__main__":
    send_mail("sribadevelopment@gmail.com")
