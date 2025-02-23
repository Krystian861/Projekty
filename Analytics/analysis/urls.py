from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="analysis/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("records/", views.record_list, name="record_list"),
    path("records/create/", views.record_create, name="record_create"),
    path("records/<int:pk>/", views.record_detail, name="record_detail"),
    path("records/<int:pk>/update/", views.record_update, name="record_update"),
    path("records/<int:pk>/delete/", views.record_delete, name="record_delete"),
    path("records/<int:pk>/toggle-favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("bulk-delete/", views.bulk_delete, name="bulk_delete"),
    path("profile/", views.profile, name="profile"),
    path("profile/settings/", views.profile_settings, name="profile_settings"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("export/", views.export_records, name="export_records"),
    path("reports/generate/", views.generate_report, name="generate_report"),
    path("assign-rank/", views.assign_rank, name="assign_rank"),
    path("ranks/", views.rank_info, name="rank_info"),
    path("activity/", views.activity_feed, name="activity_feed"),
    path("calendar/", views.calendar_view, name="calendar_view"),
    path("google/", views.google_integration, name="google_integration"),

    # Chat group URLs
    path("chat/", views.chat_group_list, name="chat_group_list"),
    path("chat/create/", views.chat_group_create, name="chat_group_create"),
    path("chat/<int:group_id>/", views.chat_group_detail, name="chat_group_detail"),
    path("chat/<int:group_id>/add/", views.chat_group_add_member, name="chat_group_add_member"),

    # File Sharing URLs
    path("files/", views.file_upload_list, name="file_upload_list"),
    path("files/create/", views.file_upload_create, name="file_upload_create"),
    path("files/<int:file_id>/", views.file_upload_detail, name="file_upload_detail"),

    # Badge & Leaderboard URLs
    path("badges/", views.badge_list, name="badge_list"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),

    # Forum URLs
    path("forum/", views.forum_topic_list, name="forum_topic_list"),
    path("forum/create/", views.forum_topic_create, name="forum_topic_create"),
    path("forum/<int:topic_id>/", views.forum_topic_detail, name="forum_topic_detail"),

    # Notification and Chat modals (handled via WebSocket) – no dodatkowych URL
    path("notifications/", views.notification_list, name="notification_list"),
]
