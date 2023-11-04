from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from supervision.models import CheckMonth, Permission


@shared_task
def check_expiry():
    now = timezone.now()
    three_days_from_now = now + timedelta(days=3)
    for perm in Permission.objects.filter(access=True):
        for month in CheckMonth.objects.filter(area=perm.area, date__lte=three_days_from_now, date__gt=now):
            email = perm.user.email
            subject = 'Уведомление о завершении срока'
            message = f'Срок проверки {month.area} заканчивается через {now.date() - month.date} дня!'
            send_mail(subject, message, 'gsuli836@gmail.com', [email])


__all__ = ('check_expiry',)  # Make sure to include the task in __all__
