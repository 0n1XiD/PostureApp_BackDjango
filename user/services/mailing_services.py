from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from user.models import User, Client


def send_mzo_mail(subject: str, to: str, msg: str = None, html_message=None) -> int:
    res = send_mail(
        subject=subject,
        message=msg,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[to],
        html_message=html_message
    )
    return res

def send_download_link_message(email: str, password: str):
    user = Client.objects.get(email=email)
    user.is_first_login = True
    user.save()
    subject = 'Welcome To Posture App!'
    html_message = render_to_string(
        'emails/registration_code.html',
        {'email': email, 'password': password}
    )
    to = user.email
    send_mzo_mail(subject=subject, html_message=html_message, to=to)


def send_reset_password_code_message(email: str):
    user = User.objects.get(email=email)
    user.create_reset_password_code()
    user.save()
    path = f'{settings.SITE_URL}reset-password/?reset_password_code={user.reset_password_code}'
    subject = 'Reset Password'
    html_message = render_to_string(
        'emails/reset_password.html',
        {'path': path}
    )
    to = user.email
    send_mail(subject=subject, html_message=html_message, to=to)