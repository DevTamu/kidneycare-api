# Generated by Django 5.2 on 2025-05-28 06:59

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_diet_plan', '0002_alter_subdietplan_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subdietplan',
            name='dish_image',
            field=models.ImageField(blank=True, null=True, storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='dish_image/'),
        ),
    ]
