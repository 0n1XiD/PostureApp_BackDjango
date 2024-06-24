from user.models import User
from user.services.auth_services import _user_validation


def delete_user(user_id: int) -> None:
    """Deletes a user by his id"""
    User.objects.get(id=user_id).delete()


def get_user(user_id: int) -> User:
    """Returns the user by his id"""
    return User.objects.get(id=user_id)


def check_user_valid(email: str) -> bool:
    return User.objects.filter(email=email).exists()


def set_user_first_login(user: User, is_generate_new: bool = False) -> None:
    if is_generate_new:
        user.is_first_login = True
        user.create_authorization_code()
        user.save()
    else:
        user.is_first_login = False
        user.authorization_code = ''
        user.save()


def change_user_info(
    user: User, first_name: str = None, last_name: str = None, email: str = None, phone: str = None,
    is_first_login: bool | None = None
) -> None:
    if email and _user_validation(email):
        user.email = email
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if phone:
        user.phone = phone
    if is_first_login:
        user.is_first_login = is_first_login
    user.save()

