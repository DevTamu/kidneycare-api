# Generated by Django 5.2 on 2025-06-22 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_chat', '0004_merge_20250610_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='status',
            field=models.CharField(choices=[('sent', 'Sent'), ('delivered', 'Delivered'), ('read', 'Read')], default='Sent', max_length=20),
        ),
    ]
