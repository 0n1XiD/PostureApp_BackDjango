from rest_framework import serializers
from .models import Chat, User, Message
from .views import get_user


# class ContactSerializer(serializers.StringRelatedField):
#     def to_internal_value(self, value):
#         return value


class UserChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'gender']


class MessageSerializer(serializers.ModelSerializer):
    author = UserChatSerializer()

    class Meta:
        model = Message
        fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    participants = UserChatSerializer(many=True)
    chat_user = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('id', 'messages', 'participants', 'chat_user')
        read_only = ('id')

    def create(self, request):
        participants = request.data.get('participants')
        chat = Chat()
        chat.save()
        for email in participants:
            contact = get_user(email)
            chat.participants.add(contact)
        chat.save()
        return chat

    def get_chat_user(self, obj):
        try:
            me = self.context['request'].user
            user = None
            for participant in obj.participants.get_queryset():
                if participant.email != me.email:
                    user = participant
            return UserChatSerializer(user).data
        except:
            return {}


class AllChatsSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    chat_user = serializers.SerializerMethodField()
    new_messages_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ('id', 'last_message', 'chat_user', 'new_messages_count')
        read_only = ('id')

    def get_last_message(self, obj):
        if obj.messages.get_queryset().last():
            last_message = obj.messages.get_queryset().last()
            return MessageSerializer(last_message).data
        return {}

    def get_chat_user(self, obj):
        try:
            me = self.context['request'].user
            user = None
            for participant in obj.participants.get_queryset():
                if participant.email != me.email:
                    user = participant
            return UserChatSerializer(user).data
        except:
            return {}

    def get_new_messages_count(self, obj):
        user = self.context['request'].user
        try:
            new_messages = len(obj.messages.filter(is_new_message=True).exclude(author=user))
            return new_messages
        except Exception as ex:
            return 0
