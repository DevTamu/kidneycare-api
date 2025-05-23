from rest_framework import serializers
from .models import DietPlan, SubDietPlan
from kidney.utils import is_field_empty
from django.db import transaction
from app_authentication.models import User


class AddDietPlanSerializer(serializers.Serializer):
    patient = serializers.CharField(required=True)
    patient_status = serializers.CharField(allow_null=True, allow_blank=True)
    meal_type = serializers.ListField(child=serializers.CharField())
    dish_image = serializers.ListField(child=serializers.ImageField())
    recipe_name = serializers.ListField(child=serializers.CharField())
    recipe_tutorial_url = serializers.ListField(child=serializers.CharField())
    recipe_description = serializers.ListField(child=serializers.CharField())
    

    def validate(self, attrs):
        
        patient_status = attrs.get('patient_status', None)
        meal_types = attrs.get('meal_type', [])
        dish_images = attrs.get('dish_image', [])
        recipe_names = attrs.get('recipe_name', [])
        recipe_tutorial_urls = attrs.get('recipe_tutorial_url', [])
        recipe_descriptions = attrs.get('recipe_description', [])

        if is_field_empty(patient_status):
            raise serializers.ValidationError({"message": "Status is required"})

        if not (len(meal_types) == len(dish_images) == len(recipe_names) == len(recipe_tutorial_urls) == len(recipe_descriptions)):
            raise serializers.ValidationError({"message": "All list fields must have the same length."})

        return attrs
    
    def create(self, validated_data):

        user_pk = validated_data.get('patient')
        patient_status = validated_data.get('patient_status')

        try:
            user_instance = User.objects.get(id=user_pk)
        except User.DoesNotExist:
            raise serializers.ValidationError({"patient": "User not found."})

        diet_plan = DietPlan.objects.create(
            patient=user_instance,
            patient_status=patient_status
        )

        meal_types = validated_data.get('meal_type', [])
        dish_images = validated_data.get('dish_image', [])
        recipe_names = validated_data.get('recipe_name', [])
        recipe_tutorial_urls = validated_data.get('recipe_tutorial_url', [])
        recipe_descriptions = validated_data.get('recipe_description', [])

        if not (len(meal_types) == len(dish_images) == len(recipe_names) == len(recipe_tutorial_urls) == len(recipe_descriptions)):
            raise serializers.ValidationError({"message": "All list fields must have the same length."})

        for i in range(len(meal_types)):
            SubDietPlan.objects.create(
                diet_plan=diet_plan,
                meal_type=meal_types[i],
                dish_image=dish_images[i],
                recipe_name=recipe_names[i],
                recipe_tutorial_url=recipe_tutorial_urls[i],
                recipe_description=recipe_descriptions[i],
            )
        
        return diet_plan


class GetPatientHealthStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['patient_status'] 


class GetPatientDietPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['id','dish_image', 'recipe_tutorial_url', 'recipe_name', 'recipe_description', 'meal_type']


class GetPatientDietPlanWithIDSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['id', 'dish_image', 'recipe_tutorial_url', 'recipe_name', 'recipe_description', 'meal_type']
