from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import redirects
from django.views import View

from .forms import PositionForm
from .models import Task
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponse
# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'ToDo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterPage(FormView):
    template_name = 'ToDo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'ToDo/task_list.html'

    def get_queryset(self):
        user = self.request.user
        search_input = self.request.GET.get('search-area') or ''
        queryset = Task.objects.filter(user=user)

        if search_input:
            queryset = queryset.filter(title__icontains=search_input)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.get_queryset()
        context['count'] = context['tasks'].filter(complete=False).count()
        context['search_input'] = self.request.GET.get('search-area') or ''
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            tasks = context['tasks']
            results = [{
                'title': task.title,
                'complete': task.complete,
                'id': task.id,
            } for task in tasks]
            return JsonResponse(results, safe=False)
        return super().render_to_response(context, **response_kwargs)

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'ToDo/task_detail.html'
    context_object_name = "task"


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')
    def form_valid(self, form):
        title = form.cleaned_data.get('title')
        description = form.cleaned_data.get('description')
        user = self.request.user
        if Task.objects.filter(title=title, description=description, user=user).exists():
            form.messages(None, ValidationError("Task with this title and description already exists."))
            return self.form_invalid(form)
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin ,DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)
        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')
            with transaction.atomic():
                self.request.user.set_task_order(positionList)
        return redirect(reverse_lazy('tasks'))