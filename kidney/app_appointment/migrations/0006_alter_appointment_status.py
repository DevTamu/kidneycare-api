# Generated by Django 5.2 on 2025-05-31 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_appointment', '0005_alter_appointment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('check-in', 'Check-In'), ('in-progress', 'In-Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('no show', 'No Show'), ('rescheduled', 'Rescheduled')], default='pending', max_length=20),
        ),
    ]
