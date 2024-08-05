from django.contrib import messages
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import MeetingForm
from .models import Meeting
import re
from django.utils import timezone


def round_to_nearest_hour(dt):
    # Przekształcamy czas na datę, aby wykonać operacje matematyczne
    dt = datetime.combine(datetime.today(), dt)

    # Zaokrąglamy do najbliższej pełnej godziny
    dt += timedelta(minutes=30)
    dt -= timedelta(minutes=dt.minute % 60, seconds=dt.second, microseconds=dt.microsecond)

    # Przekształcamy z powrotem na czas i zwracamy
    return dt.time()

def is_valid_category_name(name):
    return bool(re.match(r'^[a-zA-Z0-9\s]+$', name))

def meetings_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    return render(request, 'meetings/meetings_detail.html', {'meeting': meeting, 'on_edit_record_page': True})


def meeting_list(request):
    meetings = Meeting.objects.all()
    query = request.GET.get('q', '')

    if query:
        meetings = Meeting.objects.filter(
            title__icontains=query)

    context = {
        'meetings': meetings,
        'query': query,
    }
    return render(request, 'meetings/meetings_list.html', context)


@login_required(login_url='login')
def add_meeting(request):
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']

            # Zaokrąglanie czasu do najbliższej pełnej godziny
            rounded_time = round_to_nearest_hour(time)

            # Kombinujemy datę i czas, aby utworzyć pełną datę
            meeting_datetime = datetime.combine(date, rounded_time)

            if len(title) > 10:
                messages.error(request, "Długość nazwy spotkania nie może przekraczać 10 znaków.")
                return render(request, 'meetings/add_meeting.html', {"form": form, 'on_new_record_page': True})
            elif Meeting.objects.filter(title=title).exists():
                messages.error(request, "Już istnieje spotkanie o tej nazwie.")
                return render(request, 'meetings/add_meeting.html', {'form': form, 'on_new_record_page': True})
            elif not is_valid_category_name(title):
                messages.error(request, "Nazwa nie może zawierać znaków specjalnych.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            elif meeting_datetime > datetime.now() + timedelta(days=365):
                messages.error(request, "Spotkanie nie może odbyć się więcej niż rok.")
                return render(request, 'meetings/add_meeting.html', {'form': form, 'on_new_record_page': True})
            elif Meeting.objects.filter(date=meeting_datetime.date()).exists():
                messages.error(request, "Istnieje już spotkanie w tej dacie.")
                return render(request, 'website/new.html', {"form": form, 'on_new_record_page': True})
            elif meeting_datetime < datetime.now():
                messages.error(request, "Spotkanie nie może odbyć się wcześniej.")
                return render(request, 'meetings/add_meeting.html', {'form': form, 'on_new_record_page': True})
            elif rounded_time != time:
                messages.error(request, "Godzina musi być zaokrąglona do pełnej godziny.")
                return render(request, 'meetings/add_meeting.html', {'form': form, 'on_new_record_page': True})
            else:
                form.save()
                messages.success(request, "Spotkanie zostało dodane pomyślnie.")
                return redirect('meeting_list')
    else:
        form = MeetingForm()
    return render(request, 'meetings/add_meeting.html', {'form': form, 'on_new_record_page': True})

@login_required(login_url='login')
def edit_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)

    if request.method == 'POST':
        form4 = MeetingForm(request.POST, instance=meeting)
        if form4.is_valid():
            name = form4.cleaned_data['title']
            if Meeting.objects.exclude(pk=meeting_id).filter(title=name).exists() or not is_valid_category_name(name):
                messages.error(request, "Spotkanie o tej samej nazwie już istnieje lub nazwa zawiera nieprawidłowe znaki.")
                return render(request, 'meetings/edit_meeting.html', {'form': form4, 'on_new_record_page': True})
            form4.save()
            return redirect('meetings_detail', meeting_id=meeting_id)
    else:
        form4 = MeetingForm(instance=meeting)

    return render(request, 'meetings/edit_meeting.html', {'form': form4, 'on_new_record_page': True})

@login_required(login_url='login')
def delete_meeting(request, pk):
    meeting = get_object_or_404(Meeting, pk = pk)
    if request.method == 'POST':
        meeting.delete()
        return redirect('meeting_list')
    return render(request, 'meetings/delete_meeting.html', {'meeting': meeting, 'on_new_record_page': True})


