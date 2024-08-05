"""
URL configuration for Django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import PasswordResetCompleteView, PasswordResetConfirmView, PasswordResetDoneView
from django.urls import path, include
from projekt import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language
# from chatapp.chat.views import chat_view
from projekt.views import index, Kategoria, Czat,detail, new, new2, delete_post, edit_post, user_login, delete_kategoria, Kategoria2, edit_post2, detail2
urlpatterns = [
    #Admin
    path('admin/', admin.site.urls),
    #DRUGIURLS
    path('', include('projekt.urls')),
    #TRZECIURLS
    path('', include('projekt5.urls')),
    # #Home
    path('', index, name = "home"),
    #Kategoria
    path('kategorie', views.Kategoria2, name="kategorie"),
    #Detail
    path('detail/<int:id>', detail, name="detail"),
    path('detail2/<int:id>', views.detail2, name = "detail2"),
    # Delete
    path('website/delete/<int:id>', views.delete_post, name = "post-delete"),
    path('website/delete_kategoria/<int:id>', views.delete_kategoria, name="delete_kategoria2"),
    # Edit
    path('edit/edit/<int:id>', views.edit_post, name = "post-edit"),
    path('edit/edit2/<int:id>', views.edit_post2, name = "kategoria-edit"),
    #Dodaj
    path('website/create', views.create_post, name = 'post-create'),
    ##Formularze
    path('website/new', views.new, name = "new"),
    path('new2', views.new2, name="new2"),
    #Jakies tam urls
    path('password_reset/', views.custom_password_reset, name='password_reset'),
    path('reset/done/', views.custom_password_reset, name='password_reset_complete'),
    path('send/', views.send_message, name='send_message'),
    #Wybor
    path('i18n/setlang/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    #Język
    path('home', views.home, name='home2'),
    #Chat
    path('', include('chatApp.urls')),
    #Egzaminy - Czyli rozwiązywanie itp.
    path('', include('Egzamin.urls'))

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)