from django.db import models
from django.db.models.fields.related import OneToOneField
from accounts.models import User

# Create your models here.

class Editor(models.Model):
    user = OneToOneField(User, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + " " + self.last_nam


class Attribute(models.Model):
    name = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
