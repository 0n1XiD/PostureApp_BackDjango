from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView
)
from rest_framework.views import APIView

from chat.models import Chat
from .services import get_user, get_user_chats
from .serializers import ChatSerializer, AllChatsSerializer

User = get_user_model()


class ChatListView(APIView):

    def get(self, request):
        try:
            email = request.GET.get('email')
            if email is not None:
                contact = get_user(email)
                chats = get_user_chats(contact)
                return Response(
                    AllChatsSerializer(chats, many=True, context={'request': request}).data,
                    status=200
                )
            else:
                return Response([])
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class ChatDetailView(RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer


# class ChatCreateView(CreateAPIView):
#     queryset = Chat.objects.all()
#     serializer_class = ChatSerializer


class ChatCreateView(APIView):

    def post(self, request):
        try:
            participants = request.data.get('participants')
            chat = Chat.objects.create()
            for email in participants:
                contact = get_user(email)
                chat.participants.add(contact)
            chat.save()
            return Response(ChatSerializer(chat, context={'request': request}).data, status=200)
        except Exception as ex:
            return Response({'message': f"Error! {str(ex)}"}, status=400)


class ChatUpdateView(UpdateAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer


class ChatDeleteView(DestroyAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer