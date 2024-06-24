from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import json

from .serializers import ExerciseSerializer
from .models import Exercise
from .services import _get_all_exercises


class ShowExercises(APIView):
    def get(self, request):
        exercises = _get_all_exercises()
        serializer = ExerciseSerializer(exercises, context={'request': request}, many=True)
        return Response(serializer.data)


