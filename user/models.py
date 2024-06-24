import os
import datetime
from binascii import hexlify

from django.conf import settings
from django.core.cache import cache
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone as tz
from multiselectfield import MultiSelectField

from course.models import Week, Exercise
from rates.models import Rate


def _get_upload_user_path(instance, filename) -> str | Exception:
    try:
        if instance.status == 'client':
            return os.path.join(f'clients/{instance.client.email[0]}/client_{instance.client.id}/{filename}')
    except Exception as ex:
        return ex


def _get_upload_client_path(instance, filename) -> str | Exception:
    try:
        return os.path.join(f'clients/{instance.client.email[0]}/client_{instance.client.id}/{filename[-12:]}')
    except Exception as ex:
        return ex


class UserManager(BaseUserManager):
    """Custom user manager model"""
    use_in_migrations = True

    def _create_user(self, email, password, status='client', **extra_fields):
        user = self.model(email=email, status=status, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, status='admin', **extra_fields)


def _create_hash() -> hexlify:
    return hexlify(os.urandom(64)).decode()


class User(AbstractUser):
    """Abstract User. Used for client and moderating inheritance"""
    StatusChoices = (
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('client', 'Клиент')
    )

    GenderChoices = (
        ('male', 'Man'),
        ('female', 'Woman'),
        ('non_binary', 'Non Binary')
    )

    username = None
    email = models.EmailField('E-mail', unique=True)
    first_name = models.CharField(max_length=50, verbose_name='Name')
    last_name = models.CharField(max_length=50, verbose_name='Surname')
    avatar = models.ImageField(max_length=10000, upload_to=_get_upload_user_path, blank=True, null=True,
                               verbose_name='Avatar')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='Phone Number')
    last_visit = models.DateTimeField(verbose_name='Last Visit Date', default='2000-01-01 00:00')
    complete_day_time = models.DateTimeField(blank=True, null=True, verbose_name='Last date of exercise')
    gender = models.CharField(choices=GenderChoices, max_length=50, default='male', verbose_name='Gender')
    birthday = models.CharField(max_length=50, blank=True, null=True, verbose_name='Birth Date')
    status = models.CharField(choices=StatusChoices, max_length=100, default='client', verbose_name='Status')
    authorization_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='Authorization code')
    reset_password_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='Reset Password code')
    is_first_login = models.BooleanField(default=True, verbose_name='First Login')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['id']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def create_authorization_code(self):
        while True:
            code = _create_hash()
            if not User.objects.filter(authorization_code=code).exists():
                self.authorization_code = code
                self.save()
                break

    def create_reset_password_code(self):
        while True:
            code = _create_hash()
            if not User.objects.filter(reset_password_code=code).exists():
                self.reset_password_code = code
                self.save()
                break

    def last_seen(self):
        return cache.get('last_seen_%s' % self.email)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > (self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else:
            return False


class Client(User):
    """Client settings"""

    PostureFrontChoices = (
        ('type_var', 'Varus'),
        ('type_val', 'Valgus'),
        ('type_nor', 'Normal'),
    )

    PostureRightChoices = (
        ('type_s', 'Sway'),
        ('type_ns', 'No Sway')
    )

    height = models.SmallIntegerField(default=180, verbose_name='Height')
    weight = models.SmallIntegerField(default=70, verbose_name='Weight')

    posture_side = models.CharField(
        choices=PostureFrontChoices, max_length=100, default='type_1', verbose_name='Posture type from front side view'
    )
    posture_back = models.CharField(
        choices=PostureRightChoices, max_length=100, default='type_s', verbose_name='Posture type from right side view'
    )

    current_day = models.SmallIntegerField(default=0, verbose_name='Current Day')
    current_week = models.SmallIntegerField(default=0, verbose_name='Current Week')
    in_archive = models.BooleanField(default=False, verbose_name='In Archive')
    archive_date = models.DateTimeField(verbose_name='Archiving date', blank=True, null=True)

    # rate = models.ForeignKey(Rate, on_delete=models.CASCADE, verbose_name='Rate')
    # rate_start_day = models.DateTimeField(default=tz.now, verbose_name='Rate start day')
    # rate_end_day = models.DateTimeField(blank=True, null=True, verbose_name='Rate end day')


    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone']

    class Meta:
        ordering = ['id']
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ClientCondition(models.Model):
    """ The client's general state, sleep state, and energy state in percent and a description of them """
    client = models.ForeignKey(Client, verbose_name="Client", on_delete=models.CASCADE)
    general_condition_before = models.SmallIntegerField('General condition before exercises', null=True, blank=True)
    general_condition_after = models.SmallIntegerField('General condition after exercises', null=True, blank=True)

    def __str__(self):
        return f'{self.client.first_name} {self.client.last_name} ({self.id})'

    class Meta:
        verbose_name = "Condition"
        verbose_name_plural = "Conditions"
        ordering = ['id']


class ClientCompleteExerciseCount(models.Model):
    """Number of exercises performed on a particular day"""
    client = models.ForeignKey(Client, verbose_name="Client", on_delete=models.CASCADE)
    count = models.SmallIntegerField(default=0)
    date = models.DateField(auto_now_add=True)


class ClientPosturePhotos(models.Model):
    """ Photos of the client's posture """
    client = models.ForeignKey(Client, verbose_name="Client", on_delete=models.CASCADE)
    left_side_image = models.ImageField(max_length=10000, upload_to=_get_upload_client_path,
                                        verbose_name="Left Side Posture Photo")
    top_side_image = models.ImageField(max_length=10000, upload_to=_get_upload_client_path,
                                       verbose_name="Top Side Posture Photo")
    right_side_image = models.ImageField(max_length=10000, upload_to=_get_upload_client_path,
                                         verbose_name="Right Side Posture Photo")
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.client.first_name} {self.client.last_name} ID фотографии - {self.id}'

    class Meta:
        verbose_name = "Posture photo"
        verbose_name_plural = "Posture photos"
        ordering = ['-created_at']


class ClientWeek(models.Model):
    """Client Exercise Week"""
    name = models.CharField('Name', max_length=50)
    description = models.TextField(blank=True, null=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='client_course_weeks')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_course_user')
    is_available_for_client = models.BooleanField(default=False, verbose_name='Is Available')
    complete_count = models.SmallIntegerField(default=0, verbose_name='Days Count')

    class Meta:
        verbose_name = "Exercise Week"
        verbose_name_plural = "Exercise Weeks"
        ordering = ['id']

    def __str__(self):
        return f'Week - {self.name} Client - {self.client.first_name} {self.client.last_name}'


class ClientDay(models.Model):
    """Exercise for the week"""
    order_num = models.IntegerField('#', default=0)
    week = models.ForeignKey(ClientWeek, on_delete=models.CASCADE, blank=True, null=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, blank=True, null=True)
    sets = models.IntegerField('Set Count', default=0)
    repeats = models.IntegerField('Reps Count', default=0)
    duration = models.IntegerField('Duration (sec)', default=0)
    complete_count = models.SmallIntegerField(default=0)
    repeat_count = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "Exercise Day"
        verbose_name_plural = "Exercise Days"
        ordering = ['order_num']

    def __str__(self):
        return f'Week - {self.week.name} Client - {self.week.client.first_name} {self.week.client.last_name}'

