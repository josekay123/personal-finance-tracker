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
