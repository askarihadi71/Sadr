# Generated by Django 5.0.4 on 2024-07-30 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggerapp', '0002_logentry'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LogEntry',
        ),
    ]
