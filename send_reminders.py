import os
import django
from datetime import date, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management_system.settings')
django.setup()

# import your Django models and other utilities
from librarian.utils import send_reminder_via_email, send_reminder_via_sms
from librarian.models import Book

def send_reminder():
    current_date = date.today()
    due_date = current_date + timedelta(days=1)
    books_due_tomorrow = Book.objects.filter(due_date=due_date)

    for book in books_due_tomorrow:
            user = book.issued_to
            if user:
                email_message = f'Reminder: The book "{book.title}" is due tomorrow.'
                sms_message = f'Reminder: The book "{book.title}" is due tomorrow.'
                send_reminder_via_email(user.email, email_message)
                try:
                    send_reminder_via_sms(user.phone_number, sms_message)
                except Exception as e:
                    print(f"Failed to send SMS: {e}")    


if __name__ == "__main__":
    send_reminder()
