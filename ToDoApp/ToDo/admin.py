from django.contrib import admin
# from . import models
from .models import Task

# Register your models here.
admin.site.register(Task)