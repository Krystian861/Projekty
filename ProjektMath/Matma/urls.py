from django.urls import path
from . import views

urlpatterns = [
    path('', views.formula_list, name='home'),
    path('odkiedy/', views.odkiedy, name='odkiedy'),
    path('dokiedy/', views.dokiedy, name='dokiedy'),
    path('pomysl/', views.Pomysl, name='Pomysl'),
    path('company/', views.company, name='company'),
    path('users/', views.users, name='users'),
    path('contact/', views.contact, name='contact'),
    path('formulas/add/', views.add_formula, name='add_formula'),
    path('category/add/', views.add_category, name='add_category'),
    path('formula/<int:pk>/', views.formula_detail, name='formula_detail'),
    path('formula/<int:pk>/edit/', views.edit_formula, name='edit_formula'),
    path('formula/<int:pk>/delete/', views.delete_formula, name='delete_formula'),
    path('category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('category/<int:pk>/edit/', views.edit_category, name='edit_category'),
]
