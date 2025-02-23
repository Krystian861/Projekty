from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, DataRecord, ChatGroup, ChatMessage, FileUpload, FileComment, ForumTopic, ForumReply

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")

class DataRecordForm(forms.ModelForm):
    class Meta:
        model = DataRecord
        fields = ("title", "data", "file_type", "alert_date")

# Formy dla Chat Group
class ChatGroupForm(forms.ModelForm):
    class Meta:
        model = ChatGroup
        fields = ("name",)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa grupy'}),
        }

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ("content",)
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Wpisz wiadomość...'}),
        }

class ChatGroupAddMemberForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wpisz nazwę użytkownika'})
    )

# Formy dla File Sharing
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ("title", "file", "description", "is_featured")

class FileCommentForm(forms.ModelForm):
    class Meta:
        model = FileComment
        fields = ("comment",)

# Formy dla Forum
class ForumTopicForm(forms.ModelForm):
    class Meta:
        model = ForumTopic
        fields = ("title", "content",)

class ForumReplyForm(forms.ModelForm):
    class Meta:
        model = ForumReply
        fields = ("content",)

# Formularz ustawień profilu
class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
