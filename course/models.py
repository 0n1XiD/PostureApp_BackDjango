from django.db import models
from ckeditor.fields import RichTextField
from parler.models import TranslatableModel, TranslatedFields
from sortedm2m.fields import SortedManyToManyField


class Exercise(TranslatableModel):
    """Exercises for users"""
    translations = TranslatedFields(
        name=models.CharField(max_length=255, verbose_name="Name"),
        description=RichTextField(blank=True, null=True, verbose_name="Description", config_name='text_only'),
        video=models.FileField(upload_to='course/videos/', blank=True, null=True, verbose_name="Video File")
    )
    search_name = models.CharField(max_length=255, verbose_name="search_name")
    photo1 = models.FileField(upload_to='course/images/', blank=True, null=True, verbose_name="Exercise Photo 1")
    photo2 = models.FileField(upload_to='course/images/', blank=True, null=True, verbose_name="Exercise Photo 2")
    sets = models.IntegerField(default=0, verbose_name="Sets Amount")
    repeats = models.IntegerField(default=0, verbose_name="Reps Amount")
    duration = models.IntegerField(default=0, verbose_name="Duration")
    have_duration = models.BooleanField(default=True, verbose_name="A timed exercise?")
    have_sets = models.BooleanField(default=True, verbose_name="There is sets in exercise?")
    alternative_exercises = SortedManyToManyField('self', blank=True, verbose_name='Alternative exercises')

    def __str__(self):
        return f'{self.id} - {self.name}'

    class Meta:
        verbose_name = 'Exercise'
        verbose_name_plural = '1. Exercises'
        ordering = ['id']


class ExerciseCode(models.Model):

    name = models.CharField(max_length=255, verbose_name='Block name')
    code = models.CharField(max_length=10, verbose_name='Block code')

    def __str__(self):
        return f'Code {self.code} - {self.name}'

    class Meta:
        verbose_name = 'Exercise code'
        verbose_name_plural = '2. Exercise codes'
        ordering = ['id']

class Week(models.Model):

    """Additional exercises. Added to each user"""

    name = models.CharField(max_length=255, verbose_name='Name')
    code = models.ForeignKey(ExerciseCode, on_delete=models.CASCADE, verbose_name='Code')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = '2. Week'
        verbose_name_plural = '2. Weeks'


class WeekOrder(models.Model):
    """List of course for the week"""

    week = models.ForeignKey(Week, on_delete=models.CASCADE, blank=False, null=True, verbose_name='Week')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, blank=False, null=True, verbose_name='Exercise')
    order_num = models.IntegerField(default=0, verbose_name='Order number of the exercise')

    class Meta:
        verbose_name = 'Exercises Order in Weeks'
        ordering = ['order_num']


class ExerciseParse(models.Model):
    """Parsing exercises"""
    file = models.FileField(upload_to='parser/')

    class Meta:
        verbose_name = '3. Exercise parser'
        verbose_name_plural = '3. Exercises parser'


class WeekParse(models.Model):
    """Parsing class week"""
    file = models.FileField(upload_to='parser/')

    class Meta:
        verbose_name = 'Weeks Parser'
        verbose_name_plural = '4. Weeks Parser'

