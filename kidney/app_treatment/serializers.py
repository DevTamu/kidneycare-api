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

class PrescriptionSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'

class AccessTypeSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)
    access_type = serializers.ListField(
        child=serializers.CharField(), allow_empty=True
    )

    class Meta:
        model = AccessType
        fields = '__all__'


class TreatmentDetailsSerializer(serializers.ModelSerializer):

    treatment = serializers.CharField(read_only=True)
    time_started = serializers.TimeField(input_formats=['%H:%M'])
    time_ended = serializers.TimeField(input_formats=['%H:%M'])
    class Meta:
        model = TreatmentDetail
        fields = '__all__'


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
    last_treatment_date = serializers.DateField(input_formats=['%m-%d-%Y'])
    treatment_prescription = PrescriptionSerializer()
    treatment_access_type = AccessTypeSerializer()
    treatment_details = TreatmentDetailsSerializer()
    treatment_pre_dialysis = PreDialysisSerializer()
    treatment_post_dialysis = PostDialysisSerializer()

    class Meta:
        model = Treatment
        fields = ['diagnosis', 'nephrologist', 'last_treatment_date', 'treatment_prescription', 'treatment_access_type', 'treatment_details', 'treatment_pre_dialysis', 'treatment_post_dialysis']

    def validate(self, attrs):
        
        required_fields = [
            'diagnosis', 'nephrologist', 'last_treatment_date',
            'treatment_prescription', 'treatment_access_type',
            'treatment_details', 'treatment_pre_dialysis', 'treatment_post_dialysis'
        ]
        
        missing_fields = [field for field in required_fields if is_field_empty(attrs.get(field))]

        if missing_fields:
            errors = {"message": f"{field} is required" for field in missing_fields}
            raise serializers.ValidationError(errors)
        
        #nested serializer validation
        for field_name in [
            'treatment_prescription', 'treatment_access_type',
            'treatment_details', 'treatment_pre_dialysis', 'treatment_post_dialysis'
        ]:
            nested_data = attrs.get(field_name)
            serializer_class = self.fields[field_name].__class__
            nested_serializer = serializer_class(data=nested_data)
            if not nested_serializer.is_valid():
                raise serializers.ValidationError({"message": f"{field_name}: {nested_serializer.errors}"})
        
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

        #create the main treatment instance
        treatment = Treatment.objects.create(
            user=pk,
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