DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finance_tracker',
        'USER': 'your_username',  # Replace with your PostgreSQL username
        'PASSWORD': 'your_password',  # Replace with your PostgreSQL password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
ASGI_APPLICATION = 'finance_tracker.asgi.application'
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_tracker.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            # Add WebSocket routing here
        ])
    ),
})
from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.description}"
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Expense

@shared_task
def send_expense_reminder(user_id):
    user = User.objects.get(id=user_id)
    today = timezone.now().date()
    upcoming_expenses = Expense.objects.filter(user=user, date__gt=today)

    for expense in upcoming_expenses:
        send_mail(
            'Upcoming Expense Reminder',
            f"Reminder: You have an upcoming expense for {expense.description} of {expense.amount} scheduled for {expense.date}.",
            'from@example.com',
            [user.email],
        )
        from django.shortcuts import render
from django.http import JsonResponse
from .models import Expense, Category
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def add_expense(request):
    if request.method == "POST":
        description = request.POST['description']
        amount = request.POST['amount']
        category_id = request.POST['category']
        category = Category.objects.get(id=category_id)
        expense = Expense(user=request.user, description=description, amount=amount, category=category)
        expense.save()

        # WebSocket Notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{request.user.id}",
            {
                'type': 'expense_update',
                'message': f"New expense added: {description} for {amount}"
            }
        )

        return JsonResponse({'status': 'success', 'message': 'Expense added successfully'})

    categories = Category.objects.all()
    return render(request, 'expenses/add_expense.html', {'categories': categories})
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ExpenseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.group_name = f"user_{self.user.id}"

        # Join WebSocket group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Broadcast message to WebSocket group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'expense_update',
                'message': message
            }
        )

    # Receive message from group
    async def expense_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

