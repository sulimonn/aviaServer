# Generated by Django 4.2 on 2023-09-16 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supervision', '0007_remove_controlcard_area_checkarea_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='controlcard',
            name='area',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='supervision.checkarea'),
            preserve_default=False,
        ),
    ]
