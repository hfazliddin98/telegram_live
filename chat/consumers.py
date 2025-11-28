import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message, RoomMember
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # User autentifikatsiya qilinganligini tekshirish
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # User xona a'zosi ekanligini tekshirish
        is_member = await self.check_room_membership()
        if not is_member:
            await self.close()
            return
        
        # WebSocket ni room group ga qo'shish
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Xonaga kirganligini bildirish
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user': self.user.username,
            }
        )
    
    async def disconnect(self, close_code):
        # WebSocket ni room group dan olib tashlash
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Xonadan chiqganligini bildirish
            if hasattr(self, 'user') and self.user.is_authenticated:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_leave',
                        'user': self.user.username,
                    }
                )
    
    async def receive(self, text_data):
        """Client'dan xabar kelganda"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                content = data.get('message', '').strip()
                reply_to_id = data.get('reply_to')
                
                if content:
                    # Xabarni database ga saqlash
                    message = await self.save_message(content, reply_to_id)
                    
                    if message:
                        # Barcha group a'zolariga yuborish
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': content,
                                'user': self.user.username,
                                'user_id': self.user.id,
                                'message_id': message.id,
                                'timestamp': message.timestamp.strftime('%H:%M'),
                                'reply_to': reply_to_id,
                            }
                        )
            
            elif message_type == 'typing':
                # Typing indicator
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_typing',
                        'user': self.user.username,
                        'is_typing': data.get('is_typing', False),
                    }
                )
            
            elif message_type == 'delete_message':
                message_id = data.get('message_id')
                delete_type = data.get('delete_type', 'all')
                
                if message_id:
                    success = await self.delete_message(message_id, delete_type)
                    if success:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'message_deleted',
                                'message_id': message_id,
                                'delete_type': delete_type,
                            }
                        )
        
        except json.JSONDecodeError:
            pass
    
    async def chat_message(self, event):
        """Group'dan xabar kelganda client ga yuborish"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user': event['user'],
            'user_id': event['user_id'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
            'reply_to': event.get('reply_to'),
        }))
    
    async def user_join(self, event):
        """User xonaga kirganini bildirish"""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'user': event['user'],
        }))
    
    async def user_leave(self, event):
        """User xonadan chiqganini bildirish"""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user': event['user'],
        }))
    
    async def user_typing(self, event):
        """User yozayotganini ko'rsatish"""
        # O'ziga o'zi yubormaslik
        if event['user'] != self.user.username:
            await self.send(text_data=json.dumps({
                'type': 'user_typing',
                'user': event['user'],
                'is_typing': event['is_typing'],
            }))
    
    async def message_deleted(self, event):
        """Xabar o'chirilganini bildirish"""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'delete_type': event['delete_type'],
        }))
    
    @database_sync_to_async
    def check_room_membership(self):
        """User xona a'zosi ekanligini tekshirish"""
        try:
            room = Room.objects.get(id=self.room_id)
            return RoomMember.objects.filter(room=room, user=self.user).exists()
        except Room.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content, reply_to_id=None):
        """Xabarni database ga saqlash"""
        try:
            room = Room.objects.get(id=self.room_id)
            
            reply_to = None
            if reply_to_id:
                try:
                    reply_to = Message.objects.get(id=reply_to_id, room=room)
                except Message.DoesNotExist:
                    pass
            
            message = Message.objects.create(
                room=room,
                user=self.user,
                content=content,
                message_type='text',
                reply_to=reply_to,
            )
            return message
        except Room.DoesNotExist:
            return None
    
    @database_sync_to_async
    def delete_message(self, message_id, delete_type):
        """Xabarni o'chirish"""
        try:
            message = Message.objects.get(id=message_id, room_id=self.room_id)
            
            # Faqat xabar egasi yoki xona admini o'chira oladi
            if message.user == self.user or message.room.created_by == self.user:
                if delete_type == 'text':
                    message.content = ''
                    message.save()
                elif delete_type == 'file':
                    if message.file:
                        message.file.delete()
                        message.file = None
                        message.file_size = 0
                        message.file_type = None
                        message.save()
                elif delete_type == 'all':
                    if message.file:
                        message.file.delete()
                    message.delete()
                return True
        except Message.DoesNotExist:
            pass
        return False
