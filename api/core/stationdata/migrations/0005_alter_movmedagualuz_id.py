# Generated by Django 4.2.7 on 2024-01-18 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_stationdata', '0004_remove_movmedagualuz_example'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movmedagualuz',
            name='id',
            field=models.AutoField(default=1, max_length=30, primary_key=True, serialize=False),
        ),
    ]
