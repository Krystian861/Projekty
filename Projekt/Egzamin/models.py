from django.db import models
from django.contrib.auth.models import User

class Exam(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s answer to {self.question.text}"
