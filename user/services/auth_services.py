from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from user.models import User, Client


def generate_token(user: User) -> Token:
    """Generates and returns a token and status code. If an error occurs, it returns an error message"""
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


def client_setup_settings(
        user: Client, gender: str, height: int, weight: int
) -> None:
    """Adds basic settings to the client"""
    user.gender = gender
    user.type = type
    user.height = height
    user.weight = weight
    user.save()


def _trainer_setup_settings():
    pass


def create_user(
        email: str,
        first_name: str,
        last_name: str,
        password: str,
        phone: str = None,
        birthday: str = None
) -> tuple:
    if _user_validation(email=email) is not True:
        return {'message': "Wrong email!"}, 400
    if User.objects.filter(email=email):
        return {'message': "Account is already exist"}, 409
    user = Client.objects.create(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        phone=phone,
        birthday=birthday
    )
    return user, 200


def _user_save_base_settings(
        user: User, email: str, first_name: str, last_name: str, password: str, phone: str = None, birthday: str = None
) -> None:
    """Adds mandatory fields to the user and saves it"""
    user.email = email
    user.first_name = first_name
    user.last_name = last_name
    user.set_password(password)
    if phone:
        user.phone = phone
    if birthday:
        user.birthday = birthday
    user.save()


def _user_validation(email: str) -> bool:
    """
        user validation \n
        True - The validation was successful. \n
        False - There were errors during validation
    """
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def delete_token(user: User) -> None:
    """Deletes the current token"""
    try:
        user.auth_token.delete()
    except Exception as ex:
        pass

def change_password(user: User, password: str) -> Token:
    user.set_password(password)
    user.save()
    delete_token(user)
    return generate_token(user)


def get_user_from_auth_code(authorization_code: str) -> User:
    return User.objects.get(authorization_code=authorization_code)


def get_user_from_reset_password_code(reset_password_code: str) -> User:
    return User.objects.get(reset_password_code=reset_password_code)


def check_reset_password_valid(reset_password_code: str) -> bool:
    return User.objects.filter(reset_password_code=reset_password_code).exists()


def delete_reset_password_code(reset_password_code: str) -> None:
    if User.objects.filter(reset_password_code=reset_password_code).exists():
        user = User.objects.get(reset_password_code=reset_password_code)
        user.reset_password_code = ''
        user.save()

