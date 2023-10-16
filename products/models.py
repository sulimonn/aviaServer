from django.db import models
from django.utils.text import slugify
from users.models import User


class KindOfActivity(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Виды деятельности'
        verbose_name = 'Вид деятельности'


class Company(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='Название авиакомпании/Управленческий персонал')
    number = models.IntegerField(verbose_name="Номер СЭ")
    code = models.CharField(max_length=6, unique=True, verbose_name='3-буквен КОД ИКАО')
    validity = models.DateField(verbose_name="Срок действия сертификата эксплуатанта (СЭ)")
    status = models.BooleanField(default=True, verbose_name='Статус СЭ')
    address = models.CharField(max_length=256, unique=True, verbose_name='Адрес')
    first_phone = models.CharField(max_length=20, unique=True, verbose_name='1-номер телефона')
    second_phone = models.CharField(max_length=20, unique=True, blank=True, default=" ", verbose_name='2-номер телефона')
    email = models.CharField(max_length=64, unique=True, verbose_name='Эл. почта')
    kind_of_activity = models.ForeignKey(KindOfActivity, on_delete=models.CASCADE, verbose_name='Вид деятельности')
    slug = models.SlugField(unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Как пользователь')
    password = models.CharField(max_length=255, verbose_name='Пароль')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = "Компании"


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Company)
def create_user(sender, instance, created, **kwargs):
    from django.contrib.auth.models import Group
    if created and not instance.user:
        user = User.objects.create_user(username=instance.slug, password=instance.password)
        user.name = instance.name
        user.email = instance.email
        group = Group.objects.get(name='avia')
        user.groups.add(group)
        user.is_active = True
        user.save()
        instance.user = user
        instance.save()