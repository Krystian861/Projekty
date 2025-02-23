from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from django.utils import timezone
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from itertools import chain
from datetime import timedelta, date
from django.utils import timezone
from .models import DataRecord, FileUpload, ForumTopic, ChatMessage
from .forms import CustomUserCreationForm, DataRecordForm
from .models import DataRecord, User
# import os
#
# os.add_dll_directory(r"C:\Program Files\GTK3-Runtime Win64\bin")
#
# from weasyprint import HTML
# 
# HTML('https://weasyprint.org/').write_pdf('weasyprint-website.pdf')

def register(request):
    """Rejestracja użytkownika."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("record_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "analysis/register.html", {"form": form})


@login_required
def record_list(request):
    """
    Displays the list of records created by the logged-in user.
    Supports text search, date-range filtering, favorite filtering, and live (AJAX) updates.
    """
    query = request.GET.get("q", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    favorites_only = request.GET.get("favorites", "")

    records = DataRecord.objects.filter(created_by=request.user)

    if query:
        records = records.filter(Q(title__icontains=query) | Q(data__icontains=query))

    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            records = records.filter(created_at__date__gte=start)
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            records = records.filter(created_at__date__lte=end)
        except ValueError:
            pass

    if favorites_only == "1":
        records = records.filter(is_favorite=True)

    records = records.order_by('-created_at')
    paginator = Paginator(records, 5)  # 5 records per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
        "favorites": favorites_only,
    }

    # If this is an AJAX request, return only the records partial HTML
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('analysis/records_list_partial.html', context, request=request)
        return JsonResponse({'html': html})

    # Otherwise, render the full page
    return render(request, "analysis/record_list.html", context)

@login_required
def record_create(request):
    """Tworzenie nowego rekordu."""
    if request.method == "POST":
        form = DataRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            return redirect("record_list")
    else:
        form = DataRecordForm()
    return render(request, "analysis/record_create.html", {"form": form})


@login_required
def record_update(request, pk):
    """Edycja rekordu (tylko przez właściciela)."""
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = DataRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("record_list")
    else:
        form = DataRecordForm(instance=record)
    return render(request, "analysis/record_update.html", {"form": form, "record": record})


@login_required
def record_delete(request, pk):
    """Usuwanie rekordu (tylko przez właściciela)."""
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    if request.method == "POST":
        record.delete()
        return redirect("record_list")
    return render(request, "analysis/record_confirm_delete.html", {"record": record})


@login_required
def record_detail(request, pk):
    """Wyświetla szczegóły rekordu."""
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    return render(request, "analysis/record_detail.html", {"record": record})


@login_required
def bulk_delete(request):
    """Usuwa zaznaczone rekordy."""
    if request.method == "POST":
        record_ids = request.POST.getlist("record_ids")
        if record_ids:
            DataRecord.objects.filter(id__in=record_ids, created_by=request.user).delete()
        return redirect("record_list")
    else:
        records = DataRecord.objects.filter(created_by=request.user)
    return render(request, "analysis/bulk_delete.html", {"records": records})


@login_required
def profile(request):
    """Wyświetla profil użytkownika wraz ze statystykami."""
    user = request.user
    record_count = DataRecord.objects.filter(created_by=user).count()
    return render(request, "analysis/profile.html", {"user_profile": user, "record_count": record_count})


def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def assign_rank(request):
    """Administrator: przypisanie rangi użytkownikowi."""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        new_rank = request.POST.get("rank")
        user_to_update = get_object_or_404(User, id=user_id)
        if new_rank in dict(User.RANK_CHOICES).keys():
            user_to_update.rank = new_rank
            user_to_update.save()
            return redirect("assign_rank")
    users = User.objects.all()
    return render(request, "analysis/assign_rank.html", {"users": users, "rank_choices": User.RANK_CHOICES})


@login_required
def export_records(request):
    """Eksport rekordów użytkownika do CSV."""
    records = DataRecord.objects.filter(created_by=request.user)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="records.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Title", "Data", "Created At"])
    for record in records:
        writer.writerow([record.id, record.title, record.data, record.created_at])
    return response


@login_required
def toggle_favorite(request, pk):
    """Przełącza status ulubionego rekordu."""
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    record.is_favorite = not record.is_favorite
    record.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'is_favorite': record.is_favorite})
    return redirect('record_list')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from django.utils import timezone
import csv

from .forms import (
    CustomUserCreationForm, DataRecordForm,
    ChatGroupForm, ChatMessageForm, ChatGroupAddMemberForm,
    FileUploadForm, FileCommentForm,
    ForumTopicForm, ForumReplyForm
)
from .models import (
    DataRecord, User, ChatGroup, ChatMessage,
    FileUpload, FileComment, Badge, ForumTopic, ForumReply
)


# --- Funkcje pomocnicze (rangi, XP, badge) ---
def update_user_rank(user):
    count = DataRecord.objects.filter(created_by=user).count()
    new_rank = user.rank
    if count < 10:
        new_rank = 'beginner'
    elif count < 50:
        new_rank = 'intermediate'
    elif count < 100:
        new_rank = 'advanced'
    else:
        new_rank = 'vip'
    if new_rank != user.rank:
        user.rank = new_rank
        user.save()
        user.xp += 10
        user.save()


def rank_info(request):
    ranks = {
        'beginner': "Beginner: Dopiero zaczynasz. Utwórz więcej rekordów, aby awansować.",
        'intermediate': "Intermediate: Masz już pewne doświadczenie. Kontynuuj dobrą pracę!",
        'advanced': "Advanced: Robisz świetną robotę! Twoje umiejętności analizy danych są imponujące.",
        'vip': "VIP: Użytkownik najwyższej klasy! Jesteś mistrzem analizy danych."
    }
    context = {'ranks': ranks}
    return render(request, "analysis/rank_info.html", context)


def home(request):
    return render(request, "analysis/home.html", {})


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("record_list")
    else:
        form = CustomUserCreationForm()
    return render(request, "analysis/register.html", {"form": form})


@login_required
def record_list(request):
    query = request.GET.get("q", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    favorites_only = request.GET.get("favorites", "")

    records = DataRecord.objects.filter(created_by=request.user)

    if query:
        records = records.filter(Q(title__icontains=query) | Q(data__icontains=query))
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            records = records.filter(created_at__date__gte=start)
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            records = records.filter(created_at__date__lte=end)
        except ValueError:
            pass
    if favorites_only == "1":
        records = records.filter(is_favorite=True)

    records = records.order_by('-created_at')
    paginator = Paginator(records, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    favorite_count = DataRecord.objects.filter(created_by=request.user, is_favorite=True).count()

    notifications = DataRecord.objects.filter(
        created_by=request.user,
        alert_date__isnull=False,
        alert_date__gte=date.today(),
        alert_date__lte=date.today() + timedelta(days=3)
    )

    context = {
        "page_obj": page_obj,
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
        "favorites": favorites_only,
        "notifications": notifications,
        "favorite_count": favorite_count,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('analysis/records_list_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, "analysis/record_list.html", context)


@login_required
def record_create(request):
    if request.method == "POST":
        form = DataRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            request.user.xp += 5
            request.user.save()
            return redirect("record_list")
    else:
        form = DataRecordForm()
    return render(request, "analysis/record_create.html", {"form": form})


@login_required
def record_update(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = DataRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("record_list")
    else:
        form = DataRecordForm(instance=record)
    return render(request, "analysis/record_update.html", {"form": form, "record": record})


@login_required
def record_delete(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    if request.method == "POST":
        record.delete()
        return redirect("record_list")
    return render(request, "analysis/record_confirm_delete.html", {"record": record})


@login_required
def record_detail(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    return render(request, "analysis/record_detail.html", {"record": record})


@login_required
def bulk_delete(request):
    if request.method == "POST":
        record_ids = request.POST.getlist("record_ids")
        if record_ids:
            DataRecord.objects.filter(id__in=record_ids, created_by=request.user).delete()
        return redirect("record_list")
    else:
        records = DataRecord.objects.filter(created_by=request.user)
    return render(request, "analysis/bulk_delete.html", {"records": records})


@login_required
def profile(request):
    update_user_rank(request.user)
    record_count = DataRecord.objects.filter(created_by=request.user).count()
    return render(request, "analysis/profile.html", {"user_profile": request.user, "record_count": record_count})


def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def assign_rank(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        new_rank = request.POST.get("rank")
        user_to_update = get_object_or_404(User, id=user_id)
        if new_rank in dict(User.RANK_CHOICES).keys():
            user_to_update.rank = new_rank
            user_to_update.save()
            return redirect("assign_rank")
    users = User.objects.all()
    return render(request, "analysis/assign_rank.html", {"users": users, "rank_choices": User.RANK_CHOICES})


@login_required
def dashboard(request):
    today = timezone.now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    data_counts = []
    for day in dates:
        count = DataRecord.objects.filter(created_by=request.user, created_at__date=day).count()
        data_counts.append(count)
    dates_str = [day.strftime("%Y-%m-%d") for day in dates]
    return render(request, "analysis/dashboard.html", {"dates": dates_str, "counts": data_counts})


@login_required
def export_records(request):
    records = DataRecord.objects.filter(created_by=request.user)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="records.csv"'
    writer = csv.writer(response)
    writer.writerow(["ID", "Title", "Data", "Created At"])
    for record in records:
        writer.writerow([record.id, record.title, record.data, record.created_at])
    return response


@login_required
def toggle_favorite(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    record.is_favorite = not record.is_favorite
    record.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'is_favorite': record.is_favorite})
    return redirect('record_list')


# --- Chat Group Views ---
@login_required
def chat_group_list(request):
    groups = ChatGroup.objects.filter(members=request.user).order_by('-created_at')
    context = {"groups": groups}
    return render(request, "analysis/chat_group_list.html", context)


@login_required
def chat_group_create(request):
    if request.method == "POST":
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.leader = request.user
            group.save()
            group.members.add(request.user)
            return redirect("chat_group_detail", group_id=group.id)
    else:
        form = ChatGroupForm()
    return render(request, "analysis/chat_group_create.html", {"form": form})


@login_required
def chat_group_detail(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        return redirect("chat_group_list")
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.sender = request.user
            message.save()
            return redirect("chat_group_detail", group_id=group.id)
    else:
        form = ChatMessageForm()
    messages = group.messages.order_by("created_at")
    context = {"group": group, "messages": messages, "form": form}
    return render(request, "analysis/chat_group_detail.html", context)


@login_required
def chat_group_add_member(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        return redirect("chat_group_list")
    if request.method == "POST":
        form = ChatGroupAddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            try:
                user_to_add = User.objects.get(username=username)
                group.add_member(user_to_add)
                return redirect("chat_group_detail", group_id=group.id)
            except User.DoesNotExist:
                form.add_error("username", "User not found.")
    else:
        form = ChatGroupAddMemberForm()
    context = {"group": group, "form": form}
    return render(request, "analysis/chat_group_add_member.html", context)


# --- File Sharing Views ---
@login_required
def file_upload_list(request):
    files = FileUpload.objects.all().order_by("-created_at")
    context = {"files": files}
    return render(request, "analysis/file_upload_list.html", context)


@login_required
def file_upload_create(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            file_upload.uploaded_by = request.user
            file_upload.save()
            return redirect("file_upload_list")
    else:
        form = FileUploadForm()
    return render(request, "analysis/file_upload_create.html", {"form": form})


@login_required
def file_upload_detail(request, file_id):
    file_upload = get_object_or_404(FileUpload, id=file_id)
    if request.method == "POST":
        form = FileCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.file_upload = file_upload
            comment.commented_by = request.user
            comment.save()
            return redirect("file_upload_detail", file_id=file_upload.id)
    else:
        form = FileCommentForm()
    context = {"file": file_upload, "form": form}
    return render(request, "analysis/file_upload_detail.html", context)


# --- Badge & Leaderboard Views ---
@login_required
def badge_list(request):
    badges = Badge.objects.all()
    context = {"badges": badges}
    return render(request, "analysis/badge_list.html", context)


@login_required
def leaderboard(request):
    users = User.objects.all()
    leaderboard_data = sorted(users, key=lambda u: u.xp, reverse=True)
    context = {"leaderboard": leaderboard_data}
    return render(request, "analysis/leaderboard.html", context)


# --- Forum Views ---
@login_required
def forum_topic_list(request):
    topics = ForumTopic.objects.all().order_by("-created_at")
    context = {"topics": topics}
    return render(request, "analysis/forum_topic_list.html", context)


@login_required
def forum_topic_create(request):
    if request.method == "POST":
        form = ForumTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            return redirect("forum_topic_detail", topic_id=topic.id)
    else:
        form = ForumTopicForm()
    return render(request, "analysis/forum_topic_create.html", {"form": form})


@login_required
def forum_topic_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    if request.method == "POST":
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.created_by = request.user
            reply.save()
            return redirect("forum_topic_detail", topic_id=topic.id)
    else:
        form = ForumReplyForm()
    context = {"topic": topic, "form": form, "replies": topic.replies.order_by("created_at")}
    return render(request, "analysis/forum_topic_detail.html", context)


# --- Activity Feed ---
@login_required
def activity_feed(request):
    """
    Widok, który łączy aktywności z różnych modeli:
    - Rekordy
    - Pliki
    - Tematy Forum
    - Wiadomości czatu
    Dla każdej aktywności generowany jest słownik z danymi: data utworzenia, tytuł (lub treść),
    autor oraz URL do szczegółów.
    Aktywności są sortowane wg daty malejąco.
    """
    activities = []

    # Aktywności z rekordów
    records = DataRecord.objects.filter(created_by=request.user)
    for record in records:
        activities.append({
            'created_at': record.created_at,
            'title': record.title,
            'content': None,
            'created_by': record.created_by.username,
            'url': reverse('record_detail', args=[record.id]),
        })

    # Aktywności z plików
    files = FileUpload.objects.filter(uploaded_by=request.user)
    for file in files:
        activities.append({
            'created_at': file.created_at,
            'title': file.title,
            'content': None,
            'created_by': file.uploaded_by.username,
            'url': reverse('file_upload_detail', args=[file.id]),
        })

    # Aktywności z tematów forum
    topics = ForumTopic.objects.filter(created_by=request.user)
    for topic in topics:
        activities.append({
            'created_at': topic.created_at,
            'title': topic.title,
            'content': None,
            'created_by': topic.created_by.username,
            'url': reverse('forum_topic_detail', args=[topic.id]),
        })

    # Aktywności z wiadomości czatu (opcjonalnie – mogą generować dużo wpisów)
    messages = ChatMessage.objects.filter(sender=request.user)
    for msg in messages:
        activities.append({
            'created_at': msg.created_at,
            'title': None,
            'content': msg.content,
            'created_by': msg.sender.username,
            'url': reverse('chat_group_detail', args=[msg.group.id]),
        })

    # Sortujemy aktywności wg daty malejąco
    activities = sorted(activities, key=lambda x: x['created_at'], reverse=True)

    context = {"activities": activities}
    return render(request, "analysis/activity_feed.html", context)


# --- Calendar View ---
@login_required
def calendar_view(request):
    upcoming_records = DataRecord.objects.filter(
        created_by=request.user,
        alert_date__isnull=False,
        alert_date__gte=timezone.now().date()
    ).order_by("alert_date")
    context = {"upcoming_records": upcoming_records}
    return render(request, "analysis/calendar.html", context)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from datetime import datetime, timedelta, date
from django.utils import timezone
import csv
import weasyprint

from .forms import (
    CustomUserCreationForm, DataRecordForm,
    ChatGroupForm, ChatMessageForm, ChatGroupAddMemberForm,
    FileUploadForm, FileCommentForm,
    ForumTopicForm, ForumReplyForm, ProfileSettingsForm
)
from .models import (
    DataRecord, User, ChatGroup, ChatMessage,
    FileUpload, FileComment, Badge, ForumTopic, ForumReply, Notification
)


# Funkcje pomocnicze
def update_user_rank(user):
    count = DataRecord.objects.filter(created_by=user).count()
    new_rank = user.rank
    if count < 10:
        new_rank = 'beginner'
    elif count < 50:
        new_rank = 'intermediate'
    elif count < 100:
        new_rank = 'advanced'
    else:
        new_rank = 'vip'
    if new_rank != user.rank:
        user.rank = new_rank
        user.save()
        user.xp += 10
        user.save()







@login_required
def profile_settings(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileSettingsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileSettingsForm(instance=user)
    return render(request, 'analysis/profile_settings.html', {'form': form})


@login_required
def record_list(request):
    query = request.GET.get("q", "")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    favorites_only = request.GET.get("favorites", "")

    # Zapisywanie historii wyszukiwań
    if query:
        search_history = request.session.get('search_history', [])
        if query not in search_history:
            search_history.insert(0, query)
            if len(search_history) > 5:
                search_history = search_history[:5]
            request.session['search_history'] = search_history

    records = DataRecord.objects.filter(created_by=request.user)
    if query:
        records = records.filter(Q(title__icontains=query) | Q(data__icontains=query))
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            records = records.filter(created_at__date__gte=start)
        except ValueError:
            pass
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            records = records.filter(created_at__date__lte=end)
        except ValueError:
            pass
    if favorites_only == "1":
        records = records.filter(is_favorite=True)

    records = records.order_by('-created_at')
    paginator = Paginator(records, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    favorite_count = DataRecord.objects.filter(created_by=request.user, is_favorite=True).count()
    notifications = DataRecord.objects.filter(
        created_by=request.user,
        alert_date__isnull=False,
        alert_date__gte=date.today(),
        alert_date__lte=date.today() + timedelta(days=3)
    )

    context = {
        "page_obj": page_obj,
        "query": query,
        "start_date": start_date,
        "end_date": end_date,
        "favorites": favorites_only,
        "notifications": notifications,
        "favorite_count": favorite_count,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('analysis/records_list_partial.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, "analysis/record_list.html", context)


@login_required
def record_create(request):
    if request.method == "POST":
        form = DataRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            request.user.xp += 5
            request.user.save()
            return redirect("record_list")
    else:
        form = DataRecordForm()
    return render(request, "analysis/record_create.html", {"form": form})


@login_required
def record_update(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    if request.method == "POST":
        form = DataRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("record_list")
    else:
        form = DataRecordForm(instance=record)
    return render(request, "analysis/record_update.html", {"form": form, "record": record})


@login_required
def record_delete(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    if request.method == "POST":
        record.delete()
        return redirect("record_list")
    return render(request, "analysis/record_confirm_delete.html", {"record": record})


@login_required
def record_detail(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    return render(request, "analysis/record_detail.html", {"record": record})


@login_required
def bulk_delete(request):
    if request.method == "POST":
        record_ids = request.POST.getlist("record_ids")
        if record_ids:
            DataRecord.objects.filter(id__in=record_ids, created_by=request.user).delete()
        return redirect("record_list")
    else:
        records = DataRecord.objects.filter(created_by=request.user)
    return render(request, "analysis/bulk_delete.html", {"records": records})


@login_required
def profile(request):
    update_user_rank(request.user)
    record_count = DataRecord.objects.filter(created_by=request.user).count()
    return render(request, "analysis/profile.html", {"user_profile": request.user, "record_count": record_count})


def is_admin(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_admin)
def assign_rank(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        new_rank = request.POST.get("rank")
        user_to_update = get_object_or_404(User, id=user_id)
        if new_rank in dict(User.RANK_CHOICES).keys():
            user_to_update.rank = new_rank
            user_to_update.save()
            return redirect("assign_rank")
    users = User.objects.all()
    return render(request, "analysis/assign_rank.html", {"users": users, "rank_choices": User.RANK_CHOICES})


@login_required
def dashboard(request):
    today = timezone.now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    data_counts = [DataRecord.objects.filter(created_by=request.user, created_at__date=day).count() for day in dates]
    dates_str = [day.strftime("%Y-%m-%d") for day in dates]
    return render(request, "analysis/dashboard.html", {"dates": dates_str, "counts": data_counts})


@login_required
def export_records(request):
    records = DataRecord.objects.filter(created_by=request.user)
    export_format = request.GET.get('format', 'csv')
    response = HttpResponse(content_type="text/csv")  # Domyślnie CSV
    if export_format == 'doc':
        response = HttpResponse(content_type="application/msword")
        response['Content-Disposition'] = 'attachment; filename="records.doc"'
    elif export_format == 'pdf':
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = 'attachment; filename="records.pdf"'
    else:
        response['Content-Disposition'] = 'attachment; filename="records.csv"'

    # Dla uproszczenia, eksportujemy dane w formie tabeli tekstowej (dla DOC i PDF można wykorzystać WeasyPrint)
    writer = csv.writer(response)
    writer.writerow(["ID", "Title", "Data", "Created At"])
    for record in records:
        writer.writerow([record.id, record.title, record.data, record.created_at])
    return response


@login_required
def generate_report(request):
    records = DataRecord.objects.filter(created_by=request.user)
    html_string = render_to_string('analysis/report_template.html', {'records': records})
    html = weasyprint.HTML(string=html_string)
    pdf_file = html.write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="raport.pdf"'
    return response


@login_required
def toggle_favorite(request, pk):
    record = get_object_or_404(DataRecord, pk=pk, created_by=request.user)
    record.is_favorite = not record.is_favorite
    record.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'is_favorite': record.is_favorite})
    return redirect('record_list')


# --- Chat Group Views ---
@login_required
def chat_group_list(request):
    groups = ChatGroup.objects.filter(members=request.user).order_by('-created_at')
    context = {"groups": groups}
    return render(request, "analysis/chat_group_list.html", context)


@login_required
def chat_group_create(request):
    if request.method == "POST":
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.leader = request.user
            group.save()
            group.members.add(request.user)
            return redirect("chat_group_detail", group_id=group.id)
    else:
        form = ChatGroupForm()
    return render(request, "analysis/chat_group_create.html", {"form": form})


@login_required
def chat_group_detail(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        return redirect("chat_group_list")
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.sender = request.user
            message.save()
            return redirect("chat_group_detail", group_id=group.id)
    else:
        form = ChatMessageForm()
    messages = group.messages.order_by("created_at")
    context = {"group": group, "messages": messages, "form": form}
    return render(request, "analysis/chat_group_detail.html", context)


@login_required
def chat_group_add_member(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    if not group.members.filter(id=request.user.id).exists():
        return redirect("chat_group_list")
    if request.method == "POST":
        form = ChatGroupAddMemberForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            try:
                user_to_add = User.objects.get(username=username)
                group.add_member(user_to_add)
                return redirect("chat_group_detail", group_id=group.id)
            except User.DoesNotExist:
                form.add_error("username", "Użytkownik nie został znaleziony.")
    else:
        form = ChatGroupAddMemberForm()
    context = {"group": group, "form": form}
    return render(request, "analysis/chat_group_add_member.html", context)


# --- File Sharing Views ---
@login_required
def file_upload_list(request):
    files = FileUpload.objects.all().order_by("-created_at")
    context = {"files": files}
    return render(request, "analysis/file_upload_list.html", context)


@login_required
def file_upload_create(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_upload = form.save(commit=False)
            file_upload.uploaded_by = request.user
            file_upload.save()
            return redirect("file_upload_list")
    else:
        form = FileUploadForm()
    return render(request, "analysis/file_upload_create.html", {"form": form})


@login_required
def file_upload_detail(request, file_id):
    file_upload = get_object_or_404(FileUpload, id=file_id)
    if request.method == "POST":
        form = FileCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.file_upload = file_upload
            comment.commented_by = request.user
            comment.save()
            return redirect("file_upload_detail", file_id=file_upload.id)
    else:
        form = FileCommentForm()
    context = {"file": file_upload, "form": form}
    return render(request, "analysis/file_upload_detail.html", context)


# --- Badge & Leaderboard Views ---
@login_required
def badge_list(request):
    badges = Badge.objects.all()
    context = {"badges": badges}
    return render(request, "analysis/badge_list.html", context)


@login_required
def leaderboard(request):
    users = User.objects.all()
    leaderboard_data = sorted(users, key=lambda u: u.xp, reverse=True)
    context = {"leaderboard": leaderboard_data}
    return render(request, "analysis/leaderboard.html", context)


# --- Forum Views ---
@login_required
def forum_topic_list(request):
    topics = ForumTopic.objects.all().order_by("-created_at")
    context = {"topics": topics}
    return render(request, "analysis/forum_topic_list.html", context)


@login_required
def forum_topic_create(request):
    if request.method == "POST":
        form = ForumTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.created_by = request.user
            topic.save()
            return redirect("forum_topic_detail", topic_id=topic.id)
    else:
        form = ForumTopicForm()
    return render(request, "analysis/forum_topic_create.html", {"form": form})


@login_required
def forum_topic_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    if request.method == "POST":
        form = ForumReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.created_by = request.user
            reply.save()
            return redirect("forum_topic_detail", topic_id=topic.id)
    else:
        form = ForumReplyForm()
    context = {"topic": topic, "form": form, "replies": topic.replies.order_by("created_at")}
    return render(request, "analysis/forum_topic_detail.html", context)


# --- Activity Feed ---
@login_required
def activity_feed(request):
    from itertools import chain
    records = DataRecord.objects.filter(created_by=request.user).values("created_at", "title")
    files = FileUpload.objects.filter(uploaded_by=request.user).values("created_at", "title")
    forum_topics = ForumTopic.objects.filter(created_by=request.user).values("created_at", "title")
    chat_messages = ChatMessage.objects.filter(sender=request.user).values("created_at", "content")
    all_activities = sorted(
        chain(records, files, forum_topics, chat_messages),
        key=lambda activity: activity["created_at"],
        reverse=True
    )
    # Dla każdego obiektu aktywności ustalamy: tytuł (lub content), autora, URL
    activities = []
    for act in all_activities:
        activity = {
            'created_at': act['created_at'],
            'title': act.get('title'),
            'content': act.get('content'),
            'created_by': request.user.username,  # dla uproszczenia
            'url': '#'  # Domyślny URL, można rozbudować
        }
        activities.append(activity)
    context = {"activities": activities}
    return render(request, "analysis/activity_feed.html", context)


# --- Calendar View ---
@login_required
def calendar_view(request):
    upcoming_records = DataRecord.objects.filter(
        created_by=request.user,
        alert_date__isnull=False,
        alert_date__gte=timezone.now().date()
    ).order_by("alert_date")
    context = {"upcoming_records": upcoming_records}
    return render(request, "analysis/calendar.html", context)


# --- Google Integration ---
@login_required
def google_integration(request):
    google_calendar_url = "https://calendar.google.com/calendar/embed?src=your_calendar_id&ctz=Europe%2FWarsaw"
    google_maps_url = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d243647.53134374925!2d19.01236805!3d50.06419285!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x47165b5d6a6b40a7%3A0xa27a2b3b9f07a463!2sKrak%C3%B3w!5e0!3m2!1spl!2spl!4v1618361458692!5m2!1spl!2spl"
    context = {"google_calendar_url": google_calendar_url, "google_maps_url": google_maps_url}
    return render(request, "analysis/google_integration.html", context)


# --- Notification List ---
@login_required
def notification_list(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, "analysis/notification_list.html", {"notifications": notifications})
