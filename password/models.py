from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class PasswordRestLink(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    token = models.TextField()

    def __str__(self):
        return self.user.first_name

    