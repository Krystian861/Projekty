from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import timedelta
from django.utils.timezone import now

# Stałe wyboru typu pliku
FILE_TYPE_CHOICES = (
    ('pdf', 'PDF'),
    ('doc', 'DOC'),
    ('txt', 'TXT'),
    ('other', 'Other'),
)

# Rozszerzony model użytkownika z dodatkowymi polami (ranga, XP)
class User(AbstractUser):
    RANK_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('vip', 'VIP'),
    )
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='beginner')
    xp = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.username

# Model rekordu
class DataRecord(models.Model):
    title = models.CharField(max_length=100)
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="records"
    )
    is_favorite = models.BooleanField(default=False)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='pdf')
    alert_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} (created: {self.created_at})"

# Chat Group i Chat Message
class ChatGroup(models.Model):
    name = models.CharField(max_length=100)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="led_groups"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chat_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def add_member(self, user):
        if not self.members.filter(id=user.id).exists():
            self.members.add(user)

class ChatMessage(models.Model):
    group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg from {self.sender} in {self.group} at {self.created_at}"

# System udostępniania plików
class FileUpload(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="uploads/")
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="files")
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class FileComment(models.Model):
    file_upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="file_comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commented_by} on {self.file_upload}"

# System osiągnięć (Badge)
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to="badges/", null=True, blank=True)
    users = models.ManyToManyField(User, related_name="badges", blank=True)

    def __str__(self):
        return self.name

# Forum
class ForumTopic(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forum_topics")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ForumReply(models.Model):
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forum_replies")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.created_by} on {self.topic}"

# Powiadomienia (Notification)
class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Powiadomienie dla {self.recipient.username}: {self.message}"
