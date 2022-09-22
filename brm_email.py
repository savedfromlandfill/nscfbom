from email.message import EmailMessage
from email.utils import formataddr
import ssl
import smtplib


def send_email(email_recipients, email_subject, email_body):
    email_sender = "nscf.bom@gmail.com"
    email_password = "mxbpgtfluyddipqu"

    em = EmailMessage()
    em["From"] = formataddr(("NSCF BOM Script", email_sender))
    em["To"] = ", ".join(email_recipients)
    em["Subject"] = email_subject
    em.set_content(email_body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_recipients, em.as_string())
