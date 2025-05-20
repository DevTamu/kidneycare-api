
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('time', models.TimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Check-In', 'Check-In'), ('In-Progress', 'In-Progress'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled'), ('No Show', 'No Show'), ('Rescheduled', 'Rescheduled')], default='Pending', max_length=20)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AssignedMachine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_machine', models.CharField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=20, null=True)),
                ('assigned_machine_appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_machine_appointment', to='app_appointment.appointment')),
            ],
        ),
        migrations.CreateModel(
            name='AssignedProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_patient_appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_patient_appointment', to='app_appointment.appointment')),
                ('assigned_provider', models.ForeignKey(default=uuid.uuid4, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AssignedAppointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_appointments', to='app_appointment.appointment')),
                ('assigned_machine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_machine_appointments', to='app_appointment.assignedmachine')),
                ('assigned_provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_provider_appointment', to='app_appointment.assignedprovider')),
            ],
        ),
    ]
