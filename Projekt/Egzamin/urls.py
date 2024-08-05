from django.urls import path
from . import views

urlpatterns = [
    path('exam/<int:exam_id>/show_correct_answers/', views.show_correct_answers, name='show_correct_answers'),
    path('exam/Main_exam/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/add/', views.add_exam, name='add_exam'),
    path('exam/<int:exam_id>/edit/', views.edit_exam, name='edit_exam'),
    path('exam/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('exam/<int:exam_id>/add_question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/add_choice/', views.add_choice, name='add_choice'),
    path('exam/<int:exam_id>/solve/', views.solve_exam, name='solve_exam'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    # path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),

]
