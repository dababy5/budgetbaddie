import smtplib
from email.mime.text import MIMEText
from decouple import config

def send_sms_via_email(phone_number, carrier_domain, message):
    sender = config("EMAIL_ADDRESS")
    password = config("EMAIL_PASSWORD")

    # email-to-SMS address
    recipient = f"{phone_number}@{carrier_domain}"

    msg = MIMEText(message)
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = ""  # subject usually ignored in SMS

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        return "✅ SMS sent successfully!"
    except Exception as e:
        return f"❌ Error: {e}"
