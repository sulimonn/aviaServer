# Generated by Django 4.2 on 2023-09-18 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_rename_companies_company'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'verbose_name': 'Компания', 'verbose_name_plural': 'Компании'},
        ),
        migrations.AlterModelOptions(
            name='kindofactivity',
            options={'verbose_name': 'Вид деятельности', 'verbose_name_plural': 'Вид деятельностей'},
        ),
    ]
