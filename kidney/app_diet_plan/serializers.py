from rest_framework import serializers
from .models import DietPlan, SubDietPlan
from kidney.utils import is_field_empty
from app_authentication.models import User
from datetime import time
from django.core.validators import FileExtensionValidator


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

class CreatePatientHealthStatusSerializer(serializers.ModelSerializer):

    patient = serializers.CharField(read_only=True)

    class Meta:
        model = DietPlan
        fields = ['patient', 'patient_status', 'medication']



    def validate(self, attrs):

        pk = self.context.get('pk')

        if is_field_empty(attrs.get('patient_status')):
            raise serializers.ValidationError({"message": "Patient Status is required"})
        
        if is_field_empty(attrs.get('medication')):
            raise serializers.ValidationError({"message": "Medication is required"})
        
        user = User.objects.filter(id=pk).first()

        if not user:
            raise serializers.ValidationError({"message": "patient not found"})
        
        return attrs

    def create(self, validated_data):

        pk = self.context.get('pk')

        user = User.objects.get(id=pk)

        diet_plan_obj, _ = DietPlan.objects.update_or_create(
            patient=user,
            defaults={
                "patient_status": validated_data.get('patient_status'),
                "medication": validated_data.get('medication')
            }
        )

        return diet_plan_obj

class CreateDietPlanSerializer(serializers.Serializer):

    meal_type = serializers.CharField(required=True, error_messages={
        "blank": "Meal type cannot be empty",
        "required": "Meal type is required"
    })
    recipe_name = serializers.CharField(required=True, error_messages={
        "blank": "Recipe name cannot be empty",
        "required": "Recipe name is required"
    })
    recipe_tutorial_url = serializers.URLField(required=True, error_messages={
        "blank": "Recipe tutorial cannot be empty",
        "required": "Recipe tutorial is required"
    })
    recipe_description = serializers.CharField(required=True, error_messages={
        "blank": "Recipe description cannot be empty",
        "required": "Recipe description is required"
    })
    dish_image = serializers.ImageField(
        required=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        error_messages={
            "required": "Image is required",
            "invalid": "Invalid image"
        }
    )

    def validate(self, attrs):
        
        pk = self.context.get('pk')

        if is_field_empty(attrs.get('meal_type')):
            raise serializers.ValidationError({"message": "Meal type is required"})
        
        if is_field_empty(attrs.get('recipe_name')):
            raise serializers.ValidationError({"message": "Recipe name is required"})
        
        if is_field_empty(attrs.get('recipe_tutorial_url')):
            raise serializers.ValidationError({"message": "Recipe tutorial url is required"})
        
        if is_field_empty(attrs.get('recipe_description')):
            raise serializers.ValidationError({"message": "Recipe description is required"})
        
        if is_field_empty(attrs.get('dish_image', None)):
            raise serializers.ValidationError({"message": "Image is required"})
        
        user = User.objects.filter(id=pk).first()

        if not user:
            raise serializers.ValidationError({"message": "patient not found"})
        
        return attrs
    
    def create(self, validated_data):

        pk = self.context.get('pk')

        meal_type = validated_data.get('meal_type', None)
        dish_image = validated_data.get('dish_image', None)
        recipe_name = validated_data.get('recipe_name', None)
        recipe_tutorial_url = validated_data.get('recipe_tutorial_url', None)
        recipe_description = validated_data.get('recipe_description', None)

        # Assign time ranges based on meal type
        meal_times_mapping = {
            "Breakfast": (time(4, 0), time(10, 59)), #6:00AM - 10:59AM
            "Lunch": (time(11, 0), time(16, 59)), #11:00PM - 4:59PM
            "Dinner": (time(17, 0), time(23, 0)), #5:00PM - 11:00PM
        }

        start_time, end_time = meal_times_mapping[meal_type]

        user = User.objects.get(id=pk)

        diet_plan_obj, _ = DietPlan.objects.get_or_create(patient=user)

        SubDietPlan.objects.create(
            diet_plan=diet_plan_obj,
            meal_type=meal_type,
            dish_image=dish_image,
            recipe_name=recipe_name,
            recipe_tutorial_url=recipe_tutorial_url,
            recipe_description=recipe_description,
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
        fields = ['id', 'diet_plan', 'meal_type', 'dish_image', 'recipe_name', 'recipe_tutorial_url', 'recipe_description']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["diet_plan_id"] = data.pop('diet_plan')
        data["sub_diet_plan_id"] = data.pop('id')

        return data

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

    patient_status = serializers.SerializerMethodField()
    patient_medication = serializers.SerializerMethodField()

    class Meta:
        model = SubDietPlan
        fields = ['meal_type', 'dish_image', 'recipe_name', 'recipe_tutorial_url', 'recipe_description', 'id', 'diet_plan', 'patient_status', 'patient_medication']

    def get_patient_status(self, obj):
        return getattr(obj.diet_plan, 'patient_status', None)
    
    def get_patient_medication(self, obj):
        return getattr(obj.diet_plan, 'medication', None)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename keys
        data["diet_plan_id"] = data.pop('diet_plan')
        data["sub_diet_plan_id"] = data.pop('id')
        data["recipe_name"] = str(data.pop('recipe_name')).lower()
        data["meal_type"] = str(data.pop('meal_type')).lower()

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

class GetDietPlanStatusInProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = DietPlan
        fields = ['patient_status', 'medication']