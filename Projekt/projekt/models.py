from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class Kategoria(models.Model):
    kategoriaegzaminu = models.CharField(max_length=45)
    def __str__(self):
        return f"{self.kategoriaegzaminu}"

class Egzamin(models.Model):
    data = models.DateField()
    kategoria = models.CharField(max_length=45)
    czas = models.CharField(max_length=45)
    nazwa = models.ForeignKey(Kategoria, on_delete=models.CASCADE)


    class Meta:
        ordering = ['data']

    def __str__(self):
        return f"{self.nazwa} {self.czas} {self.kategoria} {self.data}"
