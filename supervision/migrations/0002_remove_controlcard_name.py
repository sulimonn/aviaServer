# Generated by Django 4.2 on 2023-09-15 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('supervision', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controlcard',
            name='name',
        ),
    ]
