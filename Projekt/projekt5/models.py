from django.db import models

# Create your models here.

class Meeting(models.Model):
    title = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.title} {self.time}"