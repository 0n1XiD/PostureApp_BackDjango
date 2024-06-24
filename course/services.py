import json

from django.db import transaction
from django.db.models import QuerySet
from django.template.defaultfilters import register

from .models import Exercise, Week, WeekOrder, ExerciseCode


def _get_all_exercises() -> QuerySet:
    """Returns a complete list of course"""
    return Exercise.objects.all()


@register.filter(is_safe=True)
def description_filter(value) -> str:
    """Changes the line break to the html tag <br>"""
    return value.replace('\n', '<br/>')


def parse_week_exercise(file_path):
    """Parses weeks of exercises"""
    ExerciseCode.objects.create(name="Valgus-Sway", code="VALS")
    ExerciseCode.objects.create(name="Valgus-NoSway", code="VALNS")
    ExerciseCode.objects.create(name="Varus-Sway", code="VARS")
    ExerciseCode.objects.create(name="Varus-NoSway", code="VARNS")
    ExerciseCode.objects.create(name="Normal-Sway", code="NORS")
    ExerciseCode.objects.create(name="Normal-NoSway", code="NORNS")

    with open(file_path, 'r', encoding="utf8") as file:
        week_data = json.load(file)

    for week_number, exercises in week_data.items():
        for exercise_code_name, exercise_names in exercises.items():
            if exercise_code_name in ["Valgus-Sway", "Valgus-NoSway", "Varus-Sway", "Varus-NoSway", "Normal-Sway",
                                      "Normal-NoSway"]:
                exercise_code = ExerciseCode.objects.get(name=exercise_code_name)
                week_obj, created = Week.objects.get_or_create(name=week_number, code=exercise_code)

                for index, exercise_name in enumerate(exercises.get(exercise_code.name, [])):
                    if not exercise_name:
                        continue

                    exercise_obj = Exercise.objects.filter(search_name=exercise_name.lower()).first()
                    if not exercise_obj:
                        exercise_obj = Exercise.objects.filter(search_name=exercise_name).first()

                    order_num = index
                    WeekOrder.objects.create(week=week_obj, exercise=exercise_obj, order_num=order_num)


def parse_json_to_exercise(file) -> None:
    """Parses the exercise from a file and adds it to the database"""
    with open(file, 'r', encoding="utf8") as file:
        exercise_list = json.load(file)
    for exercise in exercise_list:
        try:
            if exercise['duration']:
                have_duration = True
            else:
                exercise['duration'] = 0
                have_duration = False

            if exercise['sets']:
                have_sets = True
            else:
                exercise['sets'] = 0
                have_sets = False

            if exercise['repeats']:
                pass
            else:
                exercise['repeats'] = 0

            if exercise['duration']:
                pass
            else:
                exercise['duration'] = 0

            with transaction.atomic():
                exercise_db = Exercise.objects.create(
                    name=exercise['name_eng'],
                    description=description_filter(exercise['description_eng']),
                    search_name=f'{exercise["Unique ID"]}',
                    video=f'course/videos/{exercise["video_eng"]}',
                    photo1=f'course/images/{exercise["photo1"]}',
                    photo2=f'course/images/{exercise["photo2"]}',
                    sets=exercise['sets'],
                    repeats=exercise['repeats'],
                    duration=exercise['duration'],
                    have_duration=have_duration,
                    have_sets=have_sets
                )
                exercise_db.save()
                exercise_db.set_current_language('en')
                exercise_db.name = exercise['name_eng']
                exercise_db.description = description_filter(exercise['description_eng'])
                video = f'course/videos/{exercise["video_eng"]}'
                exercise_db.video = video
                exercise_db.save()
                exercise_db.set_current_language('kk')
                exercise_db.name = exercise['name_kz']
                exercise_db.description = description_filter(exercise['description_kz'])
                video = f'course/videos/{exercise["video_kz"]}'
                exercise_db.video = video
                exercise_db.save()
                exercise_db.set_current_language('ru')
                exercise_db.name = exercise['name_ru']
                exercise_db.description = description_filter(exercise['description_ru'])
                video = f'course/videos/{exercise["video_ru"]}'
                exercise_db.video = video
                exercise_db.save()
        except Exception as err:
            print(err)

def get_exercise_week_by_code(code: str) -> Week:
    return Week.objects.filter(code__code=code)


def get_exercise_week_order_by_week(week: Week) -> WeekOrder:
    return WeekOrder.objects.filter(week=week)



