from django.core.management.base import BaseCommand
from django.utils import timezone
from analysis.models import DataRecord
from django.core.mail import send_mail
from datetime import timedelta

class Command(BaseCommand):
    help = "Wysyła powiadomienia email dla rekordów z nadchodzącym alert_date"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        alert_records = DataRecord.objects.filter(
            alert_date__gte=today,
            alert_date__lte=today + timedelta(days=3)
        )
        for record in alert_records:
            subject = f"Alert: Rekord '{record.title}' ma nadchodzący termin"
            message = f"Rekord '{record.title}' ma ustawiony alert na {record.alert_date}.\nSprawdź go w aplikacji."
            recipient_list = [record.created_by.email]
            if record.created_by.email:
                send_mail(subject, message, 'noreply@example.com', recipient_list)
                self.stdout.write(self.style.SUCCESS(f"Powiadomienie wysłane do {record.created_by.email} dla rekordu '{record.title}'"))
