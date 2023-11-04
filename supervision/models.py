import calendar

from django.db import models
from products.models import Company
from datetime import datetime, timedelta

from users.models import User


class OversightPeriod(models.Model):
    start = models.DateField()
    end = models.DateField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    period = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.company} - {self.period}"

    class Meta:
        verbose_name = 'Период надзора'
        verbose_name_plural = 'Периоды надзора'

    def save(self, *args, **kwargs):
        _, last_day = calendar.monthrange(self.end.year, self.end.month)
        self.end = datetime(self.end.year, self.end.month, last_day).date()
        if not self.period:
            self.period = f'{self.start.year}-{self.end.year}'
        super().save(*args, **kwargs)
        if not CheckArea.objects.filter(company=self.company, period=self).exists():
            titles = [
                {
                    "title": "Летная эксплуатация(OPS)"
                },
                {
                    "title": "Система управления безопасностью полетов(SMS)"
                },
                {
                    "title": "Система качества(QMS)"
                },
                {
                    "title": "Опасные грузы(DG)"
                },
                {
                    "title": "Эксплуатационный контроль(FD)"
                },
                {
                    "title": "Кабинный экипаж(CAB)"
                },
                {
                    "title": "Авиационная безопасность(SEC)"
                },
                {
                    "title": "Летная годность(AIR)"
                },
                {
                    "title": "Подготовка персонала(PEL)"
                },
                {
                    "title": "Аэронавигационное обеспечение полетов(ANS)"
                },
                {
                    "title": "Наземное обслуживание(GH)"
                },
                {
                    "title": "Правовой статус(LEG)"
                },
                {
                    "title": "Финансово-экономическое состояние(FIN)"
                }
            ]
            for title in titles:
                check_area = CheckArea(title=title['title'], company=self.company, period=self)

                check_area.save()


class CheckArea(models.Model):
    from products.models import Company
    title = models.CharField(max_length=64)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    period = models.ForeignKey(OversightPeriod, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        i = 1
        start_date = self.period.start
        end_date = self.period.end
        while start_date <= end_date:
            _, last_day = calendar.monthrange(start_date.year, start_date.month)
            check_month = CheckMonth(
                checking=False,
                month=i,
                area=self,
                date=datetime(start_date.year, start_date.month, last_day).date()
            )
            check_month.save()
            start_date += timedelta(days=31)
            i += 1

    class Meta:
        verbose_name = "Область проверки"
        verbose_name_plural = "Области проверков"


class CheckMonth(models.Model):
    checking = models.BooleanField()
    month = models.IntegerField()
    area = models.ForeignKey(CheckArea, on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)

    def get_month_title(self):
        russian_month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь',
                               'Октябрь', 'Ноябрь', 'Декабрь']
        return russian_month_names[self.date.month - 1].lower()

    STATUS_CHOICES = (
        ('Checked', 'Проверено'),
        ('Checking', 'Проверяется'),
        ('NotChecked', 'Еще не проверено'),
        ('Moved', 'Проверка перенесена'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NotChecked')

    def __str__(self):
        return str(self.get_month_title()) + '-месяц ' + self.area.title + ' ' + self.area.company.name

    class Meta:
        verbose_name = 'Проверочный месяц'
        verbose_name_plural = 'Проверочные месяца'


class Permission(models.Model):
    from users.models import User
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    area = models.ForeignKey(CheckArea, on_delete=models.CASCADE, blank=True, null=True)
    access = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}  {self.area} {self.area.company}'

    class Meta:
        verbose_name = 'Доступ'
        verbose_name_plural = 'Доступы'


class Deadline(models.Model):
    until_the_deadline = models.IntegerField()
    first_email_sent = models.BooleanField(default=False)
    second_email_sent = models.BooleanField(default=False)
    last_email_sent = models.BooleanField(default=False)
    month = models.ForeignKey(CheckMonth, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}  {self.until_the_deadline} {self.month} {self.month.area}'