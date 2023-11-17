from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from supervision.models import CheckMonth, Permission, Deadline
from decouple import config


@shared_task
def check_deadline():
    now = timezone.now()
    for perm in Permission.objects.filter(access=True):
        for month in CheckMonth.objects.filter(area=perm.area, date__month=now.month, checking=True):
            is_deadline = Deadline.objects.filter(month__date__month=now.month, month=month, user=perm.user).exists()
            if not is_deadline:
                deadline = Deadline(user=perm.user, month=month, until_the_deadline=(month.date.day - now.day))
                deadline.save()


@shared_task
def check_expiry():
    now = timezone.now()
    for deadline in Deadline.objects.filter(month__date__month=now.month):
        if deadline.month.status != 'Checked' or deadline.month.status != 'Moved':
            email = deadline.user.email
            subject = 'Уведомление о завершении срока'
            if not deadline.first_email_sent and deadline.until_the_deadline == 10:
                message = f'Здравствуйте, {deadline.user.first_name} {deadline.user.last_name}! Срок проверки {deadline.month.area} заканчивается через 10 дней!'
                send_mail(subject, message, config('EMAIL_HOST_USER'), [email])
                deadline.first_email_sent = True

            elif not deadline.second_email_sent and deadline.until_the_deadline == 3:
                message = f'Срок проверки {deadline.month.area} заканчивается через {now.date() - deadline.month.date} дня!'
                send_mail(subject, message, config('EMAIL_HOST_USER'), [email])
                deadline.second_email_sent = True

            elif not deadline.last_email_sent and deadline.month.date == now.date():
                message = f'Срок проверки {deadline.month.area} истекaeт сегодня!'
                send_mail(subject, message, config('EMAIL_HOST_USER'), [email])
                deadline.last_email_sent = True

            deadline.until_the_deadline = deadline.month.date.day - now.day
            deadline.save()
            if deadline.until_the_deadline < 0:
                deadline.delete()
        else:
            deadline.delete()


@shared_task
def check_begins():
    now = timezone.now()
    for perm in Permission.objects.filter(access=True):
        for month in CheckMonth.objects.filter(area=perm.area, date__month=now.month, checking=True):
            if month.status != 'Checked' or month.status != 'Moved':
                email = perm.user.email
                subject = 'Уведомление о начало проверки'
                message = f'Здравствуйте, {perm.user.first_name} {perm.user.last_name}! Проверка {month.area.title} в компании {perm.area.company.name} начинается в этом месяце'
                send_mail(subject, message, config('EMAIL_HOST_USER'), [email])


__all__ = ('check_expiry', 'check_deadline', 'check_begins')
