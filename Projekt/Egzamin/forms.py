from django import forms
from .models import Exam, Question, Choice

class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
