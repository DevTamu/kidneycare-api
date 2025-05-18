from rest_framework import serializers
from .models import DietPlan
from kidney.utils import is_field_empty
from django.db import transaction

class AddDietPlanSerializer(serializers.ModelSerializer):

    patient_status = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta:
        model = DietPlan
        fields = '__all__'

    def validate(self, attrs):
        
        required_fields = ['patient', 'meal_type', 'dish_image', 'recipe_name', 'recipe_tutorial_url', 'recipe_description']

        for field in required_fields:
            if is_field_empty(attrs.get(field)):
                raise serializers.ValidationError({"message": "All fields are required to add diet plan"})

        return attrs
    
    def create(self, validated_data):
        return DietPlan.objects.create(**validated_data)
    


class GetPatientHealthStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['patient_status'] 


class GetPatientDietPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['dish_image', 'recipe_tutorial_url', 'recipe_name', 'recipe_description']



