# Generated by Django 4.2 on 2023-09-28 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supervision', '0030_alter_checklist_count_alter_checklist_files_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklist',
            name='original',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supervision.checklist'),
        ),
    ]
