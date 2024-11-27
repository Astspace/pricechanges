from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    birthday = models.DateTimeField(blank=True, null=True, verbose_name='Дата рождения')
