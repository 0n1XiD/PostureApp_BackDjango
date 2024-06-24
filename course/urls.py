from django.urls import path
from .views import ShowExercises

urlpatterns = [
    path('exercises/', ShowExercises.as_view(), name='exercises'),
]