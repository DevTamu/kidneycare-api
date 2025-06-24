from rest_framework import serializers
from .models import (
    Treatment,
    Prescription,
    AccessType,
    TreatmentDetail,
    PreDialysis,
    PostDialysis
)
from kidney.utils import is_field_empty
from app_authentication.models import User

class PrescriptionSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)

    weight_pre = serializers.FloatField(allow_null=False, error_messages={
        "null": "Weight pre cannot be empty"
    })
    weight_post = serializers.FloatField(allow_null=False, error_messages={
        "null": "Weight post cannot be empty"
    })
    pulse_pre = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Pulse pre cannot be empty"
    })
    pulse_post = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Pulse post cannot be empty"
    })
    temp_pre = serializers.FloatField(allow_null=False, error_messages={
        "null": "Temp pre cannot be empty"
    })
    temp_post = serializers.FloatField(allow_null=False, error_messages={
        "null": "Temp post cannot be empty"
    })
    respiratory_rate_pre = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Repisratory rate pre cannot be empty"
    })
    respiratory_rate_post = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Repisratory rate post cannot be empty"
    })
    saturation_percentage_pre = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Saturation percentage pre cannot be empty"
    })
    saturation_percentage_post = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Saturation percentage post cannot be empty"
    })
    rbs_pre = serializers.IntegerField(allow_null=False, error_messages={
        "null": "RBS pre cannot be empty"
    })
    rbs_post = serializers.IntegerField(allow_null=False, error_messages={
        "null": "RBS post cannot be empty"
    })
    uf_goal = serializers.FloatField(allow_null=False, error_messages={
        "null": "UF Goal cannot be empty"
    })

    class Meta:
        model = Prescription
        fields = '__all__'


class AccessTypeSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)
    access_type = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )

    class Meta:
        model = AccessType
        fields = '__all__'


class TreatmentDetailsSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)
    time_started = serializers.TimeField(format='%H:%M %p', input_formats=['%H:%M %p'], error_messages={
        "invalid": "Time Started should use of these formats: hh:mm [AM|PM]"
    })
    time_ended = serializers.TimeField(format='%H:%M %p', input_formats=['%H:%M %p'], error_messages={
        "invalid": "Time Ended should use of these formats: hh:mm [AM|PM]"
    })
    dialysis_number = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Dialysis number post cannot be empty"
    })
    machine_number = serializers.IntegerField(allow_null=False, error_messages={
        "null": "Machine number post cannot be empty"
    })

    class Meta:
        model = TreatmentDetail
        fields = '__all__'

    def to_internal_value(self, data):
        if data["time_started"] in (None, ""):
            raise serializers.ValidationError({"message": "Time started is required"})
        if data["time_ended"] in (None, ""):
            raise serializers.ValidationError({"message": "Time ended is required"})
        return super().to_internal_value(data)


class PreDialysisSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)
    class Meta:
        model = PreDialysis
        fields = '__all__'   


class PostDialysisSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)
    class Meta:
        model = PostDialysis
        fields = '__all__' 


class CreateTreatmentFormSerializer(serializers.ModelSerializer):
    # last_treatment_date = serializers.DateField(allow_null=True)
    treatment_prescription = PrescriptionSerializer()
    treatment_access_type = AccessTypeSerializer()
    treatment_details = TreatmentDetailsSerializer()
    treatment_pre_dialysis = PreDialysisSerializer()
    treatment_post_dialysis = PostDialysisSerializer()

    class Meta:
        model = Treatment
        fields = ['diagnosis', 'nephrologist', 'last_treatment_date', 'treatment_prescription', 'treatment_access_type', 'treatment_details', 'treatment_pre_dialysis', 'treatment_post_dialysis']

    def to_internal_value(self, data):

        if data["last_treatment_date"] in (None, ""):
            raise serializers.ValidationError({"message": "Last treatment date is required"})
        return super().to_internal_value(data)

    def validate(self, attrs):

        if is_field_empty(attrs.get("diagnosis")):
            raise serializers.ValidationError({"message": "Diagnosis is required"})

        if is_field_empty(attrs.get("nephrologist")):
            raise serializers.ValidationError({"message": "Nephrologist is required"})

        nested_serializer = [
            'treatment_prescription', 'treatment_access_type',
            'treatment_details', 'treatment_pre_dialysis',
            'treatment_post_dialysis'
        ]

        nested_input_data = {
            "data": {data: attrs.get(data, {}) for data in nested_serializer}
        }

        for key, data in nested_input_data["data"].items():
            for field_key, value in data.items():
                if is_field_empty(str(value)):
                    raise serializers.ValidationError({"message": f"{str(field_key).capitalize().replace('_', ' ')} is required"})
                
        return attrs

    def create(self, validated_data):
        
        #get the pk from the context
        pk = self.context.get('pk')

        #extract the nested data
        treatment_prescription_data = validated_data.pop('treatment_prescription')
        treatment_access_type_data = validated_data.pop('treatment_access_type')
        treatment_details_data = validated_data.pop('treatment_details')
        treatment_pre_dialysis_data = validated_data.pop('treatment_pre_dialysis')
        treatment_post_dialysis_data = validated_data.pop('treatment_post_dialysis')

        try:
            user = User.objects.filter(id=pk).first()
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "No user found"})

        #create the main treatment instance
        treatment = Treatment.objects.create(
            user=user,
            diagnosis=validated_data.get('diagnosis'),
            nephrologist=validated_data.get('nephrologist'),
            last_treatment_date=validated_data.get('last_treatment_date')
        )

        #create the related objects
        Prescription.objects.create(
            treatment=treatment,
            **treatment_prescription_data
        )
        AccessType.objects.create(
            treatment=treatment,
            **treatment_access_type_data
        )
        TreatmentDetail.objects.create(
            treatment=treatment,
            **treatment_details_data
        )
        PreDialysis.objects.create(
            treatment=treatment,
            **treatment_pre_dialysis_data
        )
        PostDialysis.objects.create(
            treatment=treatment,
            **treatment_post_dialysis_data
        )

        return treatment
    

class GetPatientHealthMonitoringSerializer(serializers.ModelSerializer):

    class Meta:
        model = Treatment
        fields = ['id']

    def to_representation(self, instance):

        data = super().to_representation(instance)

        user_id = self.context.get('user_id')

        treatment = Treatment.objects.get(user=user_id)

        prescription = Prescription.objects.get(
            treatment=treatment
        )

        data["weight_change"] = str(prescription.weight).lower()
        data["pre_dialysis"] = prescription.weight_pre
        data["post_dialysis"] = prescription.weight_post

        data["blood_pressure_pre_dialysis"] = str(prescription.blood_pressure_pre).replace('/', '~')
        data["blood_pressure_post_dialysis"] = str(prescription.blood_pressure_post).replace('/', '~')

        data["heart_rate_pre_dialysis"] = prescription.pulse_pre
        data["heart_rate_post_dialysis"] = prescription.pulse_post

        return data
    
class GetPatientsTreatmentHistorySerializer(serializers.ModelSerializer):

    treatment_date = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = ['user', 'treatment_date', 'id']


    def get_treatment_date(self, obj):
        return getattr(obj, 'last_treatment_date', None).strftime('%b %d, %Y')

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename keys
        data["user_id"] = data.pop('user')
        data["treatment_id"] = data.pop('id')

        return data


class GetPatientPrescriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prescription
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('treatment')

        return data

class GetPatientAccessTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccessType
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('treatment')

        return data

class GetPatientTreatmentDetailSerializer(serializers.ModelSerializer):

    time_started = serializers.TimeField(format='%H:%M %p', input_formats=['%H:%M %p'])
    time_ended = serializers.TimeField(format='%H:%M %p', input_formats=['%H:%M %p'])

    class Meta:
        model = TreatmentDetail
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('treatment')

        return data

class GetPatientPreDialysisSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreDialysis
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('treatment')

        return data


class GetPatientPostDialysisSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostDialysis
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('treatment')

        return data


class GetPatientTreatmentSerializer(serializers.ModelSerializer):

    treatment_prescription = GetPatientPrescriptionSerializer()
    treatment_access_type = GetPatientAccessTypeSerializer()
    treatment_details = GetPatientTreatmentDetailSerializer()
    treatment_pre_dialysis = GetPatientPreDialysisSerializer()
    treatment_post_dialysis = GetPatientPostDialysisSerializer()

    class Meta:
        model = Treatment
        fields = ['user', 'id', 'diagnosis', 'last_treatment_date', 'treatment_prescription', 'treatment_access_type', 'treatment_details', 'treatment_pre_dialysis', 'treatment_post_dialysis']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #renamed keys
        data["treatment_id"] = data.pop('id')
        data["user_id"] = data.pop('user')
        data["treatment_prescription"] = data.pop('treatment_prescription')
        data["treatment_access_type"] = data.pop('treatment_access_type')
        data["treatment_details"] = data.pop('treatment_details')
        data["treatment_pre_dialysis"] = data.pop('treatment_pre_dialysis')
        data["treatment_post_dialysis"] = data.pop('treatment_post_dialysis')

        return data

class DeletePatientsTreatmentHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Treatment
        fields = ['id']
    