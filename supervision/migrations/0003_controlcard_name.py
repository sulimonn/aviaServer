# Generated by Django 4.2 on 2023-09-15 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervision', '0002_remove_controlcard_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlcard',
            name='name',
            field=models.CharField(default='1', max_length=255),
        ),
    ]
