from rest_framework import serializers
from .models import DietPlan, SubDietPlan
from kidney.utils import is_field_empty
from django.db import transaction
from app_authentication.models import User
from datetime import time
import base64
import uuid
from django.core.files.base import ContentFile

class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):

        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(';base64')
            ext = format.split('/')[-1] #extract image extension
            img_data = base64.b64decode(imgstr)
            file_name = f"{uuid.uuid4()}.{ext}"
            data = ContentFile(img_data, name=file_name)


        return super().to_internal_value(data)

class SubDietPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubDietPlan
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename key
        data["diet_plan_id"] = data.pop('diet_plan')
        data["sub_diet_plan_id"] = data.pop('id')

        return data


class CreateDietPlanSerializer(serializers.Serializer):
    patient_status = serializers.CharField(allow_null=True, allow_blank=True)
    meal_type = serializers.ListField(child=serializers.CharField())
    dish_image = serializers.ListField(child=Base64ImageField())
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

        MEAL_TIME_MAPPING = {
            "Breakfast": (time(6, 0), time(11, 0)), #6-00AM - 11:00AM
            "Lunch": (time(12, 0), time(17, 0)), #12:00PM - 5:00PM
            "Dinner": (time(18, 0), time(21, 0)), #6:00PM - 9:00PM
        }

        pk = self.context.get('pk')
        patient_status = validated_data.get('patient_status')

        try:
            user_instance = User.objects.get(id=pk)
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

            meal_type = meal_types[i]

            start_time, end_time = MEAL_TIME_MAPPING.get(meal_type, (None, None))

            if start_time is None or end_time is None:
                raise serializers.ValidationError({"message": f"Invalid meal_type {meal_type}"})

            SubDietPlan.objects.create(
                diet_plan=diet_plan,
                meal_type=meal_type,
                dish_image=dish_images[i],
                recipe_name=recipe_names[i],
                recipe_tutorial_url=recipe_tutorial_urls[i],
                recipe_description=recipe_descriptions[i],
                start_time=start_time,
                end_time=end_time
            )
        
        return diet_plan


class GetPatientHealthStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['patient_status'] 


class GetPatientDietPlanLimitOneSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubDietPlan
        fields = ['diet_plan', 'meal_type', 'dish_image', 'recipe_name', 'recipe_tutorial_url', 'recipe_description']


class GetPatientDietPlanSerializer(serializers.ModelSerializer):

    diet_plan = SubDietPlanSerializer(many=True)

    class Meta:
        model = DietPlan
        fields = ['id', 'patient', 'patient_status', 'diet_plan']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename key
        data["diet_plan_id"] = data.pop('id')

        data["user_id"] = str(data.pop('patient')).replace("-", "")

        data["diet_plan"] = data.pop('diet_plan')

        return data

class GetPatientDietPlanWithIDSerializer(serializers.ModelSerializer):


    class Meta:
        model = SubDietPlan
        fields = ['id', 'diet_plan', 'meal_type', 'dish_image', 'recipe_name', 'recipe_tutorial_url', 'recipe_description']

    def to_representation(self, instance):

        data = super().to_representation(instance)

        #rename keys
        data["diet_plan_id"] = data.pop('diet_plan')
        data["sub_diet_plan_id"] = data.pop('id')

        return data