from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Expense
from django.contrib.auth.models import User

@shared_task
def send_expense_reminder(user_id):
    user = User.objects.get(id=user_id)
    today = timezone.now().date()
    upcoming_expenses = Expense.objects.filter(user=user, date__gt=today)

    for expense in upcoming_expenses:
        send_mail(
            'Upcoming Expense Reminder',
            f"Reminder: You have an upcoming expense for {expense.description} of {expense.amount} scheduled for {expense.date}.",
            'from@example.com',  # Replace with your email
            [user.email],
        )
