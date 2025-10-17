import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.dispatch import Signal
from .utilities import send_activation_notification

user_registrated = Signal(['instance'])

def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])
    
user_registrated.connect(user_registered_dispatcher)


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class AdvUser(AbstractUser):
            is_activated = models.BooleanField(default=True, db_index=True, verbose_name ='Прошел активацию?')
            send_messages = models.BooleanField (default=True, verbose_name ='Оповещать при новых комментариях?')


class AdvUsers:
    pass


def user_registrated():
    return None