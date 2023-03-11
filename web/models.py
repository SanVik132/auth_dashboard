from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(('email address'), unique=True)

class Document(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True)