import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


class AdvUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    question = models.TextField()
    password1 = models.CharField(max_length=20, blank=True)
    password2 = models.CharField(max_length=20, blank=True)


class Question(models.Model):
    title_text = models.CharField(max_length=100, default='')
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='authored_questions')
    image = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)