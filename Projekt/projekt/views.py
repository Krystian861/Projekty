from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Egzamin, Kategoria
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetForm
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import LanguageSelectionForm, PostForm, PostForm2, LoginForm, UserCreationForm
from django.forms import modelform_factory
from django.utils.translation import activate
from django.contrib.auth import authenticate, login, logout
import re
from django.utils import timezone



# Create your views here.
# def Exam(requst):
#     return render(requst, "Exam/exam.html")

def is_valid_category_name(name):
    return bool(re.match(r'^[a-zA-Z0-9\s]+$', name))

def Czat(request):
    return render(request, "website/chat.html")


def Contact(request):
    return render(request, "contact/Contact.html", {'on_edit_record_page': True})


def Kategoria2(request):
    kategorie = Kategoria.objects.all()
    query = request.GET.get('q', '')

    if query:
        kategorie = Kategoria.objects.filter(
            kategoriaegzaminu__icontains=query)

    context = {
        'Kategoria': kategorie,
        'query': query,
    }
    return render(request, "kategorie.html", context)


def detail2(request, id):
    Detail2 = get_object_or_404(Kategoria, pk = id)
    return render(request, "detail2.html", {"detail2": Detail2, 'on_edit_record_page': True})

def home_view(request):
    context = {
        'greeting': _("Welcome to our Localization Project!"),
        'large_number': 12345.67,
        'current_date': timezone.now(),
        'redirect_to': request.path
    }
    return render(request, 'detail.html', context)



def home(request):
    LANGUAGES = [
        ('en', _('English')),
        ('pl', _('Polish')),
        ('es', _('Spanish')),
        ('fr', _('French')),
    ]

    if request.method == 'POST':
        form = LanguageSelectionForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data['language']
            activate(language)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = LanguageSelectionForm()
        form.fields['language'].choices = LANGUAGES

    return render(request, 'home.html', {'form': form, 'on_new_record_page': True})


def index(request):
    egzaminy = Egzamin.objects.all()
    query = request.GET.get('q', '')

    if query:
        egzaminy = Egzamin.objects.filter(
            nazwa__kategoriaegzaminu__icontains=query)

    context = {
        'Egzamin': egzaminy,
        'query': query,
    }
    return render(request, "index.html", context)


def detail(request, id):
    Detail = get_object_or_404(Egzamin,pk = id)
    return render(request, "detail.html", {"detail": Detail, 'on_edit_record_page': True})


#Dodaj egzamin
@login_required(login_url='login')
def new(request):
    MeetingForm = modelform_factory(Egzamin, exclude=[])
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            kategoria = form.cleaned_data['kategoria']
            data_egzaminu = form.cleaned_data['data']
            if len(kategoria) > 10:
                messages.error(request, "Długość kategorii nie może przekraczać 10 znaków.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            elif Egzamin.objects.filter(kategoria=kategoria).exists():
                messages.error(request, "Taka kategoria już istnieje.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            elif not is_valid_category_name(kategoria):
                messages.error(request, "Kategoria nie może zawierać znaków specjalnych.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            elif data_egzaminu < datetime.now().date():
                messages.error(request, "Data egzaminu nie może być wcześniejsza.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            elif data_egzaminu > datetime.now().date() + timedelta(days=365):
                messages.error(request, "Data egzaminu nie może być większa niż rok.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            elif Egzamin.objects.filter(data=data_egzaminu).exists():
                messages.error(request, "Istnieje już egzamin w tej dacie.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            else:
                form.save()
                messages.success(request, "Nowy egzamin został dodany pomyślnie.")
                return redirect("home")
    else:
        form = MeetingForm()
    return render(request, "website/new.html", {"form": form, 'on_new_record_page': True})

#Dodaj kategorie
@login_required(login_url='login')
def new2(request):
    if request.method == 'POST':
        form11 = PostForm2(request.POST)
        if form11.is_valid():
            Title = form11.cleaned_data['kategoriaegzaminu']
            if len(Title) > 5:
                messages.error(request, f"Długość kategorii nie może przekraczać 5 znaków.")
                return render(request, 'website/new2.html', {"form": form11, 'on_new_record_page': True})
            elif Kategoria.objects.filter(kategoriaegzaminu=Title).exists():
                messages.error(request, "Juz takie istnieje :( ")
                return render(request, 'website/new2.html', {'form': form11, 'on_new_record_page': True})
            elif not is_valid_category_name(Title):
                messages.error(request, "Kategoria nie może zawierać znaków specjalnych.")
                return render(request, 'website/new.html', {"form": form11, 'on_new_record_page': True})
            else:
                form11.save()
                return redirect('kategorie')
    else:
        form11 = PostForm2()
        messages.success(request, "Już zostało dodane!")
    return render(request, 'website/new2.html', {'form': form11, 'on_new_record_page': True})

#Usuń Egzamin
def delete_post(request, id):
    dele = get_object_or_404(Egzamin, pk = id)
    context = {"dele": dele, 'on_edit_record_page': True}
    if request.method == 'GET':
        return render(request, 'website/delete.html', context)
    elif request.method == 'POST':
        dele.delete()
        messages.success(request, "Poprawnie usunięte")
        return redirect('home')

#Usuń Kategorie
def delete_kategoria(request, id):
    dele2 = get_object_or_404(Kategoria, pk = id)
    context2 = {"dele2": dele2, 'on_edit_record_page': True}
    if request.method == 'GET':
        return render(request, 'website/delete_kategoria.html', context2)
    elif request.method == "POST":
        dele2.delete()
        messages.success(request , "Kategoria poprawnie usunieta")
        return redirect('kategorie')

#Edytuj model
def edit_post(request, id):
    post = get_object_or_404(Egzamin, id=id)

    if request.method == "GET":
        context = {'form': PostForm(instance=post), 'id': id, 'on_edit_record_page': True}
        return render(request, 'edit/post_form.html', context)

    elif request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            name = form.cleaned_data['kategoria']
            if Egzamin.objects.exclude(pk=id).filter(kategoria=name).exists() or not is_valid_category_name(name):
                messages.error(request, "Taka nazwa kategorii już istnieje lub zawiera nieprawidłowe znaki.")
                return render(request, 'edit/post_form.html', {'form': form, 'on_new_record_page': True})
            max_length = 10
            if len(name) > max_length:
                form.add_error('data', f'Maksymalna długość danych to {max_length} znaków.')
                return render(request, 'edit/post_form.html', {'form': form})
            form.save()
            return redirect('detail', id=id)

    else:
        form = PostForm(instance=post)

    return render(request, 'edit/post_form.html', {'form': form, 'on_edit_record_page': True })


#Edytuj Kategorie

def edit_post2(request, id):
    post4 = get_object_or_404(Kategoria, id=id)

    if request.method == "GET":
        form = PostForm2(instance=post4)
        context = {'form8': form, 'id': id, 'on_edit_record_page': True}
        return render(request, 'edit/edit_post.html', context)

    elif request.method == "POST":
        form = PostForm2(request.POST, instance=post4)
        if form.is_valid():
            name = form.cleaned_data['kategoriaegzaminu']
            if Kategoria.objects.exclude(pk=id).filter(kategoriaegzaminu=name).exists() or not is_valid_category_name(name):
                messages.error(request, "Taka nazwa kategorii już istnieje lub zawiera nieprawidłowe znaki.")
                return render(request, 'edit/edit_post.html', {'form8': form, 'on_new_record_page': True})
            max_length = 10
            if len(name) > max_length:
                form.add_error('kategoriaegzaminu', f'Maksymalna długość danych to {max_length} znaków.')
                return render(request, 'edit/edit_post.html', {'form8': form})
            form.save()
            return redirect('detail2', id=id)
        else:
            messages.error(request, "Wystąpił błąd w formularzu.")
            return render(request, 'edit/edit_post.html',{'form8': form, 'on_edit_record_page': True})  # Dodajemy informację o stronie edycji rekordu


#Rejestracja
def user_signup(request):
    if request.method == 'POST':
        form6 = UserCreationForm(request.POST)
        if form6.is_valid():
            form6.save()
            return redirect('login')
    else:
        form6 = UserCreationForm()
        messages.success(request, "Rejestr poszedł poprawnie")
    return render(request, 'Login/signup.html', {'form6': form6, 'on_edit_record_page': True})

# Logowanie
def user_login(request):
    if request.method == 'POST':
        form7 = LoginForm(request.POST)
        if form7.is_valid():
            username = form7.cleaned_data['username']
            password = form7.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
    else:
        form7 = LoginForm()
        messages.success(request, "Logowanie poprawne")

    return render(request, 'Login/login.html', {'form': form7, 'on_edit_record_page': True})

#Wyloguj
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url="/login")
def profile(request):
    return render(request, 'profile.html', {'on_edit_record_page': True})

@login_required(login_url='/login')
def custom_password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return render(request, 'password_reset_done.html')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_form.html', {'form': form, 'on_new_record_page': True})

def send_message(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        if message:
            messages.add_message(request, messages.INFO, message)
    return redirect('home')

@login_required(login_url='/login')
def create_post(request):
    if request.method == 'GET':
        context2 = {'form': PostForm(), 'on_edit_record_page': True}
        return render(request, 'website/create_post.html', context2)
    elif request.method == 'POST':
        form4 = PostForm(request.POST)
        if form4.is_valid():
            form4.save()
            messages.success(request, 'The post has been created successfully. ')
            return redirect("home")
        else:
            return render(request, 'website/create_post.html', {'form': form4, 'on_edit_record_page': True})