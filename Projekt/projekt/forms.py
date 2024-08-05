from django.forms import ModelForm
from .models import Egzamin, Kategoria
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class CustomPasswordReset(PasswordResetForm):
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={'autocomplete': 'email'}))

class PostForm(ModelForm):
    class Meta:
        model = Egzamin
        fields = ['data', 'kategoria', 'nazwa', 'czas']

#
# class LanguageSelectionForm(forms.Form):
#     LANGUAGES = [
#         ('en', _('English')),
#         ('pl', _('Polish')),
#         ('es', _('Spanish')),
#         ('fr', _('French')),
#     ]
#
#     language = forms.ChoiceField(label=_('Select_language'), choices=LANGUAGES)


class LanguageSelectionForm(forms.Form):
    language = forms.ChoiceField(label=_('Select language'), choices=[])

class PostForm2(ModelForm):
    class Meta:
        model = Kategoria
        fields = '__all__'

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

