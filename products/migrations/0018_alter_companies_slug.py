# Generated by Django 4.2 on 2023-09-18 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0017_alter_companies_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companies',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]
