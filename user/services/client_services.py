import base64
import datetime
import json

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone as tz

from course.models import Exercise, Week
from course.services import get_exercise_week_by_code, get_exercise_week_order_by_week
from user.models import ClientCondition, Client, ClientPosturePhotos, ClientCompleteExerciseCount, ClientDay, ClientWeek



def _convert_base64_to_image(img):
    format, img = str(img).split(';base64,')
    ext = format.split('/')[-1] if format.split('/')[-1] != 'svg+xml' else 'svg'
    return ContentFile(base64.b64decode(img), 'photo.' + 'jpeg' if ext != 'svg' else 'svg')


def get_client(client_id: int) -> Client:
    """Returns the client by his id"""
    return Client.objects.get(id=client_id)


def update_client_complete_day_time(client: Client) -> None:
    client.complete_day_time = tz.now()
    client.save()


def reset_client_complete_day_time(client: Client) -> None:
    client.complete_day_time = None
    client.save()


def get_client_conditions(client: Client) -> ClientCondition:
    """Receives all records about the client's well-being"""
    return ClientCondition.objects.all().filter(client=client)


def add_client_condition(
        client: Client,
        general_condition_before: int, general_condition_after: str
) -> None:
    """Creates a new record of the client's well-being"""
    ClientCondition.objects.create(
        client=client,
        general_condition_before=general_condition_before,
        general_condition_after=general_condition_after
    )


def get_client_photos(client: Client) -> ClientPosturePhotos:
    return ClientPosturePhotos.objects.filter(client=client)


def add_client_photo(
    client: Client,
    left_side_image: base64,
    top_side_image: base64,
    right_side_image: base64,
) -> ClientPosturePhotos:
    new_photo_set = ClientPosturePhotos.objects.create(
        client=client,
        left_side_image=_convert_base64_to_image(left_side_image),
        top_side_image=_convert_base64_to_image(top_side_image),
        right_side_image=_convert_base64_to_image(right_side_image)
    )
    return new_photo_set


def change_client_photo(photo_id: int, photo: base64, line_first: int, line_second: int):
    client_photo = ClientPosturePhotos.objects.get(id=photo_id)
    client_photo.image = _convert_base64_to_image(photo)
    client_photo.top_line_first = line_first
    client_photo.top_line_second = line_second
    client_photo.save()


def delete_client_photo(photo_id: int) -> None:
    ClientPosturePhotos.objects.get(id=photo_id).delete()


def get_client_complete_exercise_count(client: Client) -> ClientCompleteExerciseCount:
    """Returns an array of exercises performed on specific days"""
    return ClientCompleteExerciseCount.objects.all().filter(client=client)


def add_client_complete_exercise_count(client: Client) -> None:
    """Add a completed exercise (if there were no completed exercises today, it creates a new object)"""
    if ClientCompleteExerciseCount.objects.filter(client=client, date=datetime.date.today()):
        complete_exercise = ClientCompleteExerciseCount.objects.get(client=client, date=datetime.date.today())
        complete_exercise.count += 1
        complete_exercise.save()
    else:
        ClientCompleteExerciseCount.objects.create(client=client, count=1)


def get_client_week(client: Client) -> ClientWeek:
    return ClientWeek.objects.filter(client=client)

def get_client_week_by_id(week_id: int) -> ClientWeek:
    return ClientWeek.objects.get(id=week_id)

def add_client_week(
        client: Client,
        name: str,
        week: Week,
        description: str = None,
        is_available_for_client: bool = False,
) -> ClientWeek:
    return ClientWeek.objects.create(
        client=client,
        name=name,
        week=week,
        description=description,
        is_available_for_client=is_available_for_client,
        complete_count=0
    )

def complete_client_week(week_id: int, client: Client, is_repeat: None) -> None:
    week = ClientWeek.objects.get(id=week_id)
    days = ClientDay.objects.filter(week=week)
    for day in days:
        day.repeat_count = 0
        day.save()
    if not is_repeat:
        week.complete_count += 1
        client.current_day += 1
        if client.current_day >= 7:
            client.current_day = 0
            client.current_week += 1
            reset_client_complete_day_time(client)
        client.save()
        week.save()


def update_client_week(week_id: int, description: str, name: str, open_for_client: bool,
                       open_for_trainer: bool) -> None:
    week = ClientWeek.objects.get(id=week_id)
    week.description = description
    week.name = name
    week.is_available_for_client = open_for_client
    week.is_available_for_trainer = open_for_trainer
    week.save()


def get_client_day(client: Client, week_id: int) -> ClientDay:
    return ClientDay.objects.filter(week__client=client, week__id=week_id)


def add_client_day(week_id: int, exercise_id: int, repeats: int = 0, sets: int = 0, duration: int = 0) -> ClientDay:
    if ClientDay.objects.filter(week_id=week_id).exists():
        order_num = ClientDay.objects.filter(week_id=week_id)
        order_num = order_num.last().order_num + 1
    else:
        order_num = 0
    return ClientDay.objects.create(
        order_num=order_num,
        week_id=week_id,
        exercise_id=exercise_id,
        repeats=repeats,
        sets=sets,
        duration=duration
    )


def change_client_day(
        day_id: int,
        exercise_id: int = None,
        repeats: int = None,
        sets: int = None,
        duration: int = None,
        order_num: int = None
) -> ClientDay:
    day = ClientDay.objects.get(id=day_id)
    if exercise_id:
        day.exercise = Exercise.objects.get(id=exercise_id)
    if repeats:
        day.repeats = repeats
    if sets:
        day.sets = sets
    if duration:
        day.duration = duration
    if order_num:
        day.order_num = order_num
    day.save()
    return day


def complete_client_day(day_id: int, is_repeat: bool = None) -> None:
    day = ClientDay.objects.get(id=day_id)
    if is_repeat:
        day.repeat_count += 1
    else:
        day.complete_count += 1
    day.save()


def previous_client_day(day_id: int, is_repeat: bool = None) -> None:
    if is_repeat:
        day = ClientDay.objects.get(id=day_id)
        day.repeat_count -= 1
    else:
        day = ClientDay.objects.get(id=day_id)
        day.complete_count -= 1
    day.save()


def delete_client_day(day_id: int) -> None:
    ClientDay.objects.get(id=day_id).delete()



def create_client_condition(
        client: Client,
        general_condition_before: int, general_condition_after: int
) -> None:
    ClientCondition.objects.create(
        client=client,
        general_condition_before=general_condition_before,
        general_condition_after=general_condition_after
    )


def change_client_last_visit(client: Client) -> None:
    client.last_visit = tz.now()
    client.save()


def add_client_to_archive(client: Client) -> None:
    client.in_archive = True
    client.archive_date = tz.now()
    client.save()

def reset_all_weeks_for_current_client(client: Client):
    weeks = get_client_week(client)
    client.current_week = 0
    client.current_day = 0
    client.save()
    for week in weeks:
        week.complete_count = 0
        week.complete_count_exercises = 0
        week.is_available_for_client = False
        week.save()
    weeks[0].is_available_for_client = True
    weeks[0].save()
    reset_client_complete_day_time(client)


def generate_client_weeks_exercises(client_id: int):
    client = Client.objects.get(id=client_id)
    print(123)
    week_code = f"{client.posture_side.replace('type_', '').upper()}" \
            f"{client.posture_back.replace('type_', '').upper()}"
    print(week_code)
    for index, set in enumerate(get_exercise_week_by_code(code=week_code)):
        client_week = add_client_week(
            client=client,
            name=f'Week {index + 1}',
            week=set,
            is_available_for_client=True if index == 0 else False,
        )
        for ex in get_exercise_week_order_by_week(week=set):
            add_client_day(
                week_id=client_week.id,
                exercise_id=ex.exercise.id,
                repeats=ex.exercise.repeats,
                sets=ex.exercise.sets,
                duration=ex.exercise.duration
            )