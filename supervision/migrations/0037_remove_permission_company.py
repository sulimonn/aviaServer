# Generated by Django 4.2 on 2023-09-29 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supervision', '0036_permission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='company',
        ),
    ]
