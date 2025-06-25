from django.db import models
from kidney.models import TimestampModel
from app_authentication.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
class DietPlan(TimestampModel):

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_diet_plan')
    patient_status = models.CharField(null=True, blank=True)
    medication = models.TextField(max_length=10000, null=True, blank=True)

    def __str__(self):
        return f'{self.patient.username} Diet Plan'
    
class SubDietPlan(models.Model):

    meal_type_choices = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner')
    ]

    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, null=True, blank=True, related_name='diet_plan')
    meal_type = models.CharField(null=True, blank=True, choices=meal_type_choices)
    dish_image = models.ImageField(max_length=500, storage=MediaCloudinaryStorage(), upload_to='dish_image/', blank=True, null=True)
    recipe_name = models.CharField(null=True, blank=True)
    recipe_tutorial_url = models.URLField(max_length=255, null=True, blank=True)
    recipe_description = models.TextField(max_length=10000, null=True, blank=True)
    start_time = models.TimeField(null=True)   
    end_time = models.TimeField(null=True)   

    class Meta:
        unique_together = ('meal_type',)


