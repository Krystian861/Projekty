from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DataRecord, ChatGroup, ChatMessage, FileUpload, FileComment, Badge, ForumTopic, ForumReply, Notification

admin.site.register(User, UserAdmin)
admin.site.register(DataRecord)
admin.site.register(ChatGroup)
admin.site.register(ChatMessage)
admin.site.register(FileUpload)
admin.site.register(FileComment)
admin.site.register(Badge)
admin.site.register(ForumTopic)
admin.site.register(ForumReply)
admin.site.register(Notification)
