from django.urls import path
from . import views

urlpatterns = [
    path('chat/index6/', views.HomePage, name='home4'),
    path('chat/Chat/<str:room_name>/<str:username>/', views.MessageView, name='room'),
    path('chat/delete_room/<str:room_name>/', views.delete_room, name='delete_room'),
    path('chat/room/<str:room_name>/edit/', views.edit_room, name='edit_room'),

]