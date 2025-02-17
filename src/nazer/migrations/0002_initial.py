# Generated by Django 5.0.6 on 2024-10-29 12:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('nazer', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='alarm',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nazer.device'),
        ),
        migrations.AddIndex(
            model_name='alarm',
            index=models.Index(fields=['time'], name='nazer_alarm_time_5a8a13_idx'),
        ),
        migrations.AddIndex(
            model_name='alarm',
            index=models.Index(fields=['device_name'], name='nazer_alarm_device__fd173f_idx'),
        ),
        migrations.AddIndex(
            model_name='alarm',
            index=models.Index(fields=['alarm_name'], name='nazer_alarm_alarm_n_437586_idx'),
        ),
        migrations.AddIndex(
            model_name='alarm',
            index=models.Index(fields=['alarm_type'], name='nazer_alarm_alarm_t_93ef30_idx'),
        ),
        migrations.AddIndex(
            model_name='alarm',
            index=models.Index(fields=['ip'], name='nazer_alarm_ip_85ba14_idx'),
        ),
    ]
