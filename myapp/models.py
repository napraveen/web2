from django.db import models
from datetime import datetime

# Create your models here.
class Details(models.Model):
    username =  models.CharField(max_length=100, blank=True)
