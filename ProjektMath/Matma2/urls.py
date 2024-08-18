from django.urls import path
from . import views

urlpatterns = [
    path('home2/', views.formula_list2, name='home2'),
    path('web/formulas2/add/', views.add_formula2, name='add_formula2'),
    path('web/category2/add/', views.add_category2, name='add_category2'),
    path('web/formula2/<int:pk>/delete/', views.delete_formula2, name='delete_formula2'),
    path('web/category2/<int:pk>/delete/', views.delete_category2, name='delete_category2'),
    path('web/formulas2/<int:pk>/', views.formula_detail2, name='formula_detail2'),
    path('web/formula2/edit/<int:pk>/', views.edit_formula2, name='edit_formula2'),
    path('web/category2/<int:pk>/edit/', views.edit_category2, name='edit_category2'),
]
