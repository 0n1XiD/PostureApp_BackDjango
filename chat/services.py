from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Chat

User = get_user_model()


def get_last_20_messages(chatId):
    chat = get_object_or_404(Chat, id=chatId)
    return chat.messages.order_by('-timestamp').all()[:20]


def set_messages_read(chatId, user):
    chat = get_object_or_404(Chat, id=chatId)
    messages = chat.messages.order_by('-timestamp').filter(is_new_message=True)
    for message in messages:
        if message.author != user:
            message.is_new_message = False
            message.save()


def get_user(email):
    return get_object_or_404(User, email=email)


def get_current_chat(chatId):
    return get_object_or_404(Chat, id=chatId)


def get_new_messages_count(chatId):
    return get_object_or_404(Chat, id=chatId)


def get_user_chats(user):
    try:
        chat = user.chats.all()
        return chat
    except:
        return []
