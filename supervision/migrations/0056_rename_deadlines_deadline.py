# Generated by Django 4.2 on 2023-10-20 14:53

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supervision', '0055_deadlines'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Deadlines',
            new_name='Deadline',
        ),
    ]