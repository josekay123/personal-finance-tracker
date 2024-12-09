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
