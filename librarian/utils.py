from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
            
def send_otp_via_email(email, otp):
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp}',
        'dev.purpose24@gmail.com',
        [email],
        fail_silently=False,
    )
    print(f"Sending OTP {otp} to email {email}")

def send_otp_via_sms(phone_number, otp):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    print(f"Sending SMS to {phone_number}")  # Debugging line
    message = client.messages.create(
        body=f"Your OTP is {otp}",
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number  # Ensure this is in E.164 format
    )
    return message

def send_reminder_via_email(email, email_message):
    send_mail(
        'Book Return Reminder',
        email_message,
        'dev.purpose24@gmail.com',
        [email],
        fail_silently=False,
    )
    print(f"Sending reminder to email {email}")

def send_reminder_via_sms(phone_number, sms_message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    print(f"Sending SMS to {phone_number}")  # Debugging line
    message = client.messages.create(
        body = sms_message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number  # Ensure this is in E.164 format
    )
    return message