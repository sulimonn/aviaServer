from django.db import models

from supervision.models import CheckMonth, CheckArea


# Create your models here.
def upload_to_checklist(instance, filename):
    return f'uploads/checklists/{filename}'


def upload_to_letter_to_avia(instance, filename):
    return f'uploads/to-avia/{filename}'


def upload_to_pkd(instance, filename):
    return f'uploads/PKD/{filename}'


def upload_to_fine_protocol(instance, filename):
    return f'uploads/Fine-Protocol/{filename}'


def upload_to_letter_from_avia(instance, filename):
    return f'uploads/from-avia/{filename}'


def upload_to_approval(instance, filename):
    return f'uploads/Approval/{filename}'


def upload_to_report(instance, filename):
    return f'uploads/Report/{filename}'


def upload_to_notification(instance, filename):
    return f'uploads/Notification/{filename}'


def upload_to_elimination(instance, filename):
    return f'uploads/Notification/{filename}'


def upload_to_moved(instance, filename):
    return f'uploads/Moved/{filename}'


class Checklist(models.Model):
    count = models.IntegerField(null=True, blank=True)
    month = models.ForeignKey(CheckMonth, on_delete=models.CASCADE, null=True, blank=True)
    files = models.FileField(upload_to=upload_to_checklist, verbose_name='Контрольная карта')
    comment = models.BooleanField()
    area = models.ForeignKey(CheckArea, on_delete=models.CASCADE, null=True, blank=True)
    original = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.files.name)

    def save(self, *args, **kwargs):
        if self.original:
            self.month = self.original.month
            self.area = self.original.area
            self.count = self.original.count + 1
        else:
            self.count = 1
        super().save(*args, **kwargs)
        if self.comment and self.month:
            self.month.status = 'Checking'
            self.month.save()
        if not self.original and not self.comment and self.month:
            self.month.status = 'Checked'
            self.month.save()
        if self.count == 3:
            self.month.status = 'NotChecked'
            self.month.save()

    def delete(self, using=None, keep_parents=False):
        month = self.month
        month.status = 'NotChecked'
        month.save()
        super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        verbose_name = 'Контрольная карта'
        verbose_name_plural = 'Контрольные карты'


class Prescription(models.Model):
    letter = models.FileField(upload_to=upload_to_letter_to_avia)
    fine_protocol = models.FileField(upload_to=upload_to_fine_protocol, blank=True, null=True)
    checklist = models.ForeignKey(Checklist, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'Предписание {self.checklist.area.title}'

    class Meta:
        verbose_name = 'Предписание'
        verbose_name_plural = 'Предписания'


class PKD(models.Model):
    letter = models.FileField(upload_to=upload_to_letter_from_avia)
    pkd = models.FileField(upload_to=upload_to_pkd)
    checklist = models.ForeignKey(Checklist, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pkd.name)

    class Meta:
        verbose_name = 'ПКД'
        verbose_name_plural = 'ПКД'


class Approval(models.Model):
    approval = models.FileField(upload_to=upload_to_approval)
    deadline = models.DateField()
    checklist = models.ForeignKey(Checklist, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.approval.name)

    class Meta:
        verbose_name = 'Одобрение'
        verbose_name_plural = 'Одобрения'


class Elimination(models.Model):

    letter = models.FileField(upload_to=upload_to_elimination)
    checklist = models.ForeignKey(Checklist, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.letter.name)


class Report(models.Model):
    report = models.FileField(upload_to=upload_to_report)
    checklist = models.ForeignKey(Checklist, null=True, blank=True, on_delete=models.CASCADE)

    def save(self, *args, ** kwargs):
        super().save(*args, **kwargs)
        self.checklist.month.status = 'Checked'
        self.checklist.month.save()

    def __str__(self):
        return str(self.report.name)


class Notification(models.Model):
    letter = models.FileField(upload_to=upload_to_notification)
    checklist = models.ForeignKey(Checklist, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.letter.name)


class Moved(models.Model):
    area = models.ForeignKey(CheckArea, on_delete=models.CASCADE, blank=True, null=True)
    month = models.ForeignKey(CheckMonth, on_delete=models.CASCADE, blank=True, null=True)
    raport = models.FileField(upload_to=upload_to_moved)

    class Meta:
        verbose_name = 'Рапорт'
        verbose_name_plural = 'Рапорты'
