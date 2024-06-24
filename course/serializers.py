from parler_rest.fields import TranslatedFieldsField
from rest_framework import serializers
from parler_rest.serializers import TranslatableModelSerializer
from .models import Exercise, Week, WeekOrder


class ExerciseSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Exercise)
    class Meta:
        model = Exercise
        fields = "__all__"


class ExerciseWeekOrderSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer()

    class Meta:
        model = WeekOrder
        fields = "__all__"


class ExerciseWeekSerializer(serializers.ModelSerializer):
    exercises = ExerciseWeekOrderSerializer(source='weekorder_set', many=True)

    class Meta:
        model = Week
        fields = "__all__"
