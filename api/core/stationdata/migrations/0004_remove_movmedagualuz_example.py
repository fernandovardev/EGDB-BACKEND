# Generated by Django 4.2.7 on 2024-01-18 16:29

from django.db import migrations


class Migration(migrations.Migration):


    dependencies = [
        ('core_stationdata', '0003_movmedagualuz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movmedagualuz',
            name='EXAMPLE',
        ),
    ]
