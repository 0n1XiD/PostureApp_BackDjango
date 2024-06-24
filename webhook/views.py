import random
import string

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from user.services.auth_services import create_user
from user.services.mailing_services import send_download_link_message


def generate_password(length):
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(length))
    return password

class ClickFunnelsWebhookView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        data = request.data
        email_address = data['data']['attributes']['email_address']
        first_name = data['data']['attributes']['first_name']
        last_name = data['data']['attributes']['last_name']
        generated_password = generate_password(12)
        try:
            user, status_code = create_user(
                email=email_address,
                first_name=first_name,
                last_name=last_name,
                password=generated_password,
            )
            if status_code != 200:
                return Response(user, status=status_code)
            send_download_link_message(email_address, generated_password)
        except Exception as ex:
            return Response({'message': f'Error! {str(ex)}'}, 400)

        return Response("Success")
