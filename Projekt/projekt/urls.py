from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    #login

    path('login/', views.user_login, name='login'),
    #rejestracja
    path('signup/', views.user_signup, name='signup'),
    #Wylogowywanie
    path('logout/', views.user_logout, name='logout'),
    #Egzamin
    # path('exam/', views.Exam, name = 'exam/'),
    #Kontakt
    path('contact/', views.Contact, name='Contact'),
    #Profil
    path('profile/', views.profile, name='profile'),

    #chat

]