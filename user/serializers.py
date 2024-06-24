from rest_framework import serializers

from course.serializers import ExerciseSerializer
from .models import User, Client, ClientWeek, ClientPosturePhotos, ClientCompleteExerciseCount, ClientCondition, ClientDay
from rates.serializers import RateSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password",)


class ClientPosturePhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPosturePhotos
        fields = "__all__"


class ClientCompleteExerciseCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCompleteExerciseCount
        fields = "__all__"


class ClientConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientCondition
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("password", "user_permissions", "groups", "date_joined", 'authorization_code')


class ClientWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientWeek
        fields = '__all__'


class ClientDaySerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(many=False)

    class Meta:
        model = ClientDay
        fields = "__all__"

