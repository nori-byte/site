from django.contrib import admin
from .models import Question, Choice, AdvUser


admin.site.register(Question)
admin.site.register(AdvUser)
admin.site.register(Choice)