from django.db import models

# Create your models here.

class Config(models.Model):
    version = models.CharField(max_length=32)
    mf = models.CharField(max_length=32)
    encoding = models.CharField(max_length=32)
    title_page = models.CharField(max_length=255)
    noframes = models.TextField()