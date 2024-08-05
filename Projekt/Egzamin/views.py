from django.shortcuts import render, redirect, get_object_or_404
from .models import Exam, Question, Choice, UserAnswer
from .forms import ExamForm, QuestionForm, ChoiceForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages
import re

def is_valid_category_name(name):
    return bool(re.match(r'^[a-zA-Z0-9\s]+$', name))

@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    exam_id = question.exam.id

    if request.method == 'POST':
        exam_id = question.exam.id
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect('exam_detail', exam_id=exam_id)

    return render(request, 'exam/delete_question_confirmation.html', {'question': question, 'on_edit_record_page': True})

def show_correct_answers(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)

    if UserAnswer.objects.filter(user=request.user, question__exam=exam).exists():
        return render(request, 'exam/show_correct_answers.html', {'exam': exam})
    else:
        messages.error(request, 'Możesz sprawdzić odpowiedzi dopiero po rozwiązaniu!')
        return redirect('exam_list')

@login_required
def exam_list(request):
    exams = Exam.objects.all()
    query = request.GET.get('q', '')

    if query:
        exams = Exam.objects.filter(
            title__icontains=query)

    return render(request, 'exam/exam_list.html', {'exams': exams, 'query': query})

@login_required
def exam_detail(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)

    return render(request, 'exam/exam_detail.html', {'exam': exam, 'on_new_record_page': True})

@login_required
def add_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            new_exam_title = form.cleaned_data['title']
            if Exam.objects.filter(title=new_exam_title).exists() or not is_valid_category_name(new_exam_title):
                messages.error(request, 'Nazwa egzaminu już istnieje lub zawiera nieprawidłowe znaki.')
            else:
                form.save()
                return redirect('exam_list')
    else:
        form = ExamForm()
    return render(request, 'exam/add_exam.html', {'form': form, 'on_new_record_page': True})

@login_required(login_url='login')
def add_question(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        choice_forms = [ChoiceForm(request.POST, prefix=str(x)) for x in range(4)]
        if question_form.is_valid() and all(form.is_valid() for form in choice_forms):
            question = question_form.save(commit=False)
            question.exam = exam
            if not exam.question_set.filter(text=question.text).exists() and is_valid_category_name(question.text):
                question.save()
                for form in choice_forms:
                    if form.cleaned_data.get('text'):
                        choice = form.save(commit=False)
                        choice.question = question
                        choice.save()
                return redirect('exam_detail', exam_id=exam.id)
            else:
                messages.error(request, "Juz istnieje takie pytanie lub nazwa pytania zawiera nieprawidłowe znaki.")
                return render(request, 'exam/add_question.html', {'question_form': question_form, 'choice_forms': choice_forms, 'exam': exam, 'on_new_record_page': True})
    else:
        question_form = QuestionForm()
        choice_forms = [ChoiceForm(prefix=str(x)) for x in range(4)]
    return render(request, 'exam/add_question.html', {'question_form': question_form, 'choice_forms': choice_forms, 'exam': exam, 'on_new_record_page': True})

@login_required
def add_choice(request, question_id):
    question = Question.objects.get(pk=question_id)
    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid() and is_valid_category_name(form.cleaned_data['text']):
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('exam_detail', exam_id=question.exam.id)
        else:
            messages.error(request, "Nazwa odpowiedzi zawiera nieprawidłowe znaki.")
    else:
        form = ChoiceForm()
    return render(request, 'exam/add_choice.html', {'form': form, 'question': question})

def solve_exam(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    questions = exam.question_set.all()
    if not questions.exists():
        messages.error(request, "Nie można rozwiązać tego egzaminu, ponieważ nie ma żadnych pytań.")
        return redirect('exam_list')

    if UserAnswer.objects.filter(user=request.user, question__exam=exam).exists():
        messages.error(request, "Nie możesz już tutaj wejść.")
        return redirect('exam_list')

    if request.method == 'POST':
        answered_questions = set()
        score = 0
        for question in questions:
            selected_choices = request.POST.getlist(f'question_{question.id}')
            if selected_choices:
                answered_questions.add(question.id)
            correct_choices = question.choice_set.filter(is_correct=True).values_list('id', flat=True)
            if set(selected_choices) == set(map(str, correct_choices)):
                score += 1

        if len(answered_questions) < len(questions):
            messages.error(request, "Musisz odpowiedzieć na wszystkie pytania, aby zakończyć egzamin.")
            return redirect('solve_exam', exam_id=exam_id)

        for question in questions:
            selected_choices = request.POST.getlist(f'question_{question.id}')
            for choice_id in selected_choices:
                choice = Choice.objects.get(pk=choice_id)
                UserAnswer.objects.create(question=question, choice=choice, user=request.user)

        return redirect(reverse('exam_detail', args=[exam.id]) + f'?score={score}')

    return render(request, 'exam/solve_exam.html', {'exam': exam, 'questions': questions})

def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            new_exam_title = form.cleaned_data['title']
            if Exam.objects.exclude(pk=exam_id).filter(title=new_exam_title).exists() or not is_valid_category_name(new_exam_title):
                messages.error(request, 'Egzamin o tej nazwie już istnieje lub nazwa zawiera nieprawidłowe znaki.')
                return render(request, 'exam/edit_exam.html', {'form': form,  'on_edit_record_page': True})
            form.save()
            messages.success(request, "Egzamin został pomyślnie zaktualizowany.")
            return redirect('exam_list')
    else:
        form = ExamForm(instance=exam)


    return render(request, 'exam/edit_exam.html', {'form': form, 'exam': exam, 'on_edit_record_page': True})

@login_required
def delete_exam(request, exam_id):
    exam = Exam.objects.get(pk=exam_id)
    if request.method == 'POST':
        exam.delete()
        messages.success(request, "Egzamin został pomyślnie usunięty.")
        return redirect('exam_list')
    return render(request, 'exam/delete_exam_confirmation.html', {'exam': exam, 'on_new_record_page': True})
