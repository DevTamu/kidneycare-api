
# Generated by Django 5.2 on 2025-06-02 02:06

# Generated by Django 5.2 on 2025-06-02 01:58


import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_diet_plan', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dietplan',
            name='medication',
            field=models.TextField(blank=True, max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='subdietplan',
            name='dish_image',
            field=models.ImageField(blank=True, null=True, storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to='dish_image/'),
        ),
        migrations.AlterField(
            model_name='subdietplan',
            name='end_time',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='subdietplan',
            name='recipe_description',
            field=models.TextField(blank=True, max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='subdietplan',
            name='recipe_tutorial_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='subdietplan',
            name='start_time',
            field=models.TimeField(null=True),
        ),
    ]
