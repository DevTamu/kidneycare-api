from rest_framework import serializers
from .models import DietPlan, SubDietPlan
from kidney.utils import is_field_empty
from app_authentication.models import User
from datetime import time
from django.core.validators import FileExtensionValidator
from collections import defaultdict

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

    patient_status = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    medication = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )
    meal_type = serializers.ListField(
        child=serializers.CharField(
            allow_null=False,
            allow_blank=False,
            error_messages={"blank": "Meal type is required"}
        )   
    )
    dish_image = serializers.ListField(
        child=serializers.ImageField(
            required=True,
            allow_null=True,
            allow_empty_file=False,
            validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
            error_messages={
                'required': 'Please upload a image.',
                'invalid': 'Please upload a image.',
            }
        ),
    )

    recipe_name = serializers.ListField(child=serializers.CharField(
            allow_null=False,
            allow_blank=False,
            error_messages={"blank": "Recipe name is required"}
        )
    )
    recipe_tutorial_url = serializers.ListField(child=serializers.URLField(
            allow_null=False,
            allow_blank=False,
            error_messages={"blank": "Recipe tutorial url is required"}
        )
    )
    recipe_description = serializers.ListField(child=serializers.CharField(
            allow_null=False,
            allow_blank=False,
            error_messages={"blank": "Recipe description is required"}
        )
    )

    def validate(self, attrs):
    
        meal_types = attrs.get('meal_type', [])
        dish_images = attrs.get('dish_image', [])
        recipe_names = attrs.get('recipe_name', [])
        recipe_tutorial_urls = attrs.get('recipe_tutorial_url', [])
        recipe_descriptions = attrs.get('recipe_description', [])
        
        if is_field_empty(recipe_names):
            raise serializers.ValidationError({"message": "Recipe name is required"})
        
        if is_field_empty(recipe_tutorial_urls):
            raise serializers.ValidationError({"message": "Recipe tutorial url is required"})
        
        if is_field_empty(recipe_descriptions):
            raise serializers.ValidationError({"message": "Recipe description is required"})
        
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


        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            raise serializers.ValidationError({"patient": "User not found."})

        diet_plan_obj, created = DietPlan.objects.update_or_create(
            patient=user,
            defaults={
                "patient_status": validated_data.get('patient_status', None),
                "medication": validated_data.get('medication', None)
            }
        )

        meal_types = validated_data.get('meal_type', [])
        dish_images = validated_data.get('dish_image', [])
        recipe_names = validated_data.get('recipe_name', [])
        recipe_tutorial_urls = validated_data.get('recipe_tutorial_url', [])
        recipe_descriptions = validated_data.get('recipe_description', [])

        for i in range(len(meal_types)):

            meal_type = meal_types[i]

            start_time, end_time = MEAL_TIME_MAPPING.get(meal_type, (None, None))

            if start_time is None or end_time is None:
                raise serializers.ValidationError({"message": "Invalid meal_type"})

            if created:
                SubDietPlan.objects.create(
                    diet_plan=diet_plan_obj,
                    meal_type=meal_type,
                    dish_image=dish_images[i],
                    recipe_name=recipe_names[i],
                    recipe_tutorial_url=recipe_tutorial_urls[i],
                    recipe_description=recipe_descriptions[i],
                    start_time=start_time,
                    end_time=end_time
                )
        
        return diet_plan_obj
        

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

        data["user_id"] = str(data.pop('patient'))

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
    

class GetDietPlanInAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['patient', 'patient_status', 'medication', 'id']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename keys
        data["patient_id"] = str(data.pop('patient'))
        data["diet_plan_id"] = data.pop('id')

        return data
    

class GetAllDietPlansInAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubDietPlan
        fields = ['diet_plan', 'id', 'meal_type', "dish_image", "recipe_name"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename keys
        data["diet_plan_id"] = data.pop('diet_plan')
        data["sub_diet_plan_id"] = data.pop('id')

        #lowercase the response
        data["meal_type"] = str(data.pop('meal_type')).lower()
        data["recipe_name"] = str(data.pop('recipe_name')).lower()


        return data
    

class GetPatientMedicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['patient', 'patient_status', 'medication', 'id']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["patient_id"] = str(data.pop('patient'))
        data["medication_id"] = data.pop('id')

        return data