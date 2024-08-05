from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import meeting_list, add_meeting, edit_meeting, delete_meeting, meetings_detail

urlpatterns = [

    path('meet/meetings/', views.meeting_list, name = "meeting_list"),
    path('meetings/add', views.add_meeting, name="add_meeting"),
    path('meetings/edit/<int:meeting_id>', views.edit_meeting, name="edit_meeting"),
    path('meetings/detail/<int:meeting_id>', views.meetings_detail, name='meetings_detail'),
    path('meetings/delete/<int:pk>', views.delete_meeting, name="delete_meeting"),
    path('', include('django.contrib.auth.urls')),
]