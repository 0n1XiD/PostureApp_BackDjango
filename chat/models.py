from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Message(models.Model):
    author = models.ForeignKey(
        User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_new_message = models.BooleanField(default=True)

    def __str__(self):
        return self.author.email


class Chat(models.Model):
    participants = models.ManyToManyField(
        User, related_name='chats', blank=True)
    messages = models.ManyToManyField(Message, blank=True)

    def __str__(self):
        return f'{self.pk}'
