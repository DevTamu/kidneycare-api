from django.db import models
from kidney.models import TimestampModel
from app_authentication.models import User

class DietPlan(TimestampModel):

    meal_type_choices = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    ]
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_diet_plan')
    patient_status = models.CharField(null=True, blank=True)
    meal_type = models.CharField(null=True, blank=True, choices=meal_type_choices)
    dish_image = models.ImageField(upload_to='dish_image/', blank=True, null=True)
    recipe_name = models.CharField(null=True, blank=True)
    recipe_tutorial_url = models.CharField(max_length=255, null=True, blank=True)
    recipe_description = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.patient.username} Diet Plan'


