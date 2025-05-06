from rest_framework import serializers
from rest_framework import status
from .models import Appointment, AssignedAppointment, AssignedMachine
from kidney.utils import is_field_empty
from django.db import transaction
import logging
from app_authentication.models import User
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


class CreateAssignedAppointmentSerializer(serializers.Serializer):
    assigned_provider = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )
    assigned_machine = serializers.ListField(
        child=serializers.CharField(), allow_empty=False
    )

class CreateAppointmentSerializer(serializers.ModelSerializer):

    date_time = serializers.DateTimeField(allow_null=True, input_formats=["%B %d, %Y - %I:%M %p"])
    status = serializers.CharField(allow_blank=True, allow_null=True)
    assigned_appointment = CreateAssignedAppointmentSerializer()
    
    class Meta:
        model = Appointment
        fields = ['date_time', 'status', 'assigned_appointment']

    def validate(self, attrs):

        MAX_MACHINE_AVAILABLE = 10

        #get the request from the conttext
        request = self.context.get('request')

        appointment_fields = attrs.get('assigned_appointment', {})

        current_user_logged_in = User.objects.get(id=request.user.id)

        #raise an error only if not "Patient" role
        if current_user_logged_in.role != 'Patient':
            raise serializers.ValidationError({"message": "Only patients are allowed to book an appointment."})

        #checking if the fields are empty
        if is_field_empty(attrs.get('status')):
            raise serializers.ValidationError({"message": "Status is required"})
        
        if is_field_empty(appointment_fields["assigned_provider"]):
            raise serializers.ValidationError({"message": "Provider must not be empty"})
        
        if is_field_empty(appointment_fields["assigned_machine"]):
            raise serializers.ValidationError({"message": "Machine must not be empty"})
        
        firstnames = [
            name.split(" ", 1)[0].strip()  # Take the part before the first space
            for name in appointment_fields.get("assigned_provider", [])
        ]

        #get all existing first names from the database that match those in the 'firstnames' list
        exist_firstname = User.objects.filter(first_name__in=firstnames).values_list('first_name', flat=True)
        
        #get the list of first names that do not exist in the database
        invalid_firstnames = [firstname for firstname in firstnames if firstname not in exist_firstname]

        #raise a validation error if any first names were not found in the database
        if invalid_firstnames:
            raise serializers.ValidationError({"message": "Provider not found"})
        
        machines_used = [
            machine.strip() 
            for machine in appointment_fields.get('assigned_machine', [])
        ]

        all_occupied_machines  = AssignedMachine.objects.filter(status="Occupied").values_list('assigned_machine', flat=True)

        occupied_machines_flat = [machine for sublist in all_occupied_machines for machine in (sublist or [])]

        #check if any machine in machines_used is already occupied
        conflicting_machines = [machine for machine in machines_used if machine in occupied_machines_flat]


        if conflicting_machines:
            raise serializers.ValidationError({"message": "This machine is in used"})

        return attrs

    @transaction.atomic
    def create(self, validated_data):

        # Extract nested appointment assignment data
        assigned_data = validated_data.pop('assigned_appointment', {})

        #get the request from the context
        request = self.context.get('request')

        #create the AppointmentAssigned instance linked to the user
        create_appointment = Appointment.objects.create(
            user=request.user,
            date_time=validated_data.get('date_time'),
            status=validated_data.get('status')
        )

        assigned_appointment_machine = AssignedMachine.objects.create(
            assigned_machine=assigned_data.get('assigned_machine'),
            status="Occupied"
        )

        #create the AppointmentAssigned instance linked to the created appointment
        appointment_assigned = AssignedAppointment.objects.create(
            appointment=create_appointment,
            assigned_machine=assigned_appointment_machine
        )

        #set the assigned provider and machine from the provided data
        appointment_assigned.assigned_provider = assigned_data.get('assigned_provider')
        appointment_assigned.save()

        return create_appointment
    
class GetAssignedMachineInProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignedMachine
        fields = ['assigned_machine', 'status']


class GetAssignedAppointmentInProviderSerializer(serializers.ModelSerializer):
    assigned_provider = serializers.SerializerMethodField()
    assigned_machine = serializers.SerializerMethodField()
    # get_assigned_machine = GetAssignedMachineInProviderSerializer(many=True)

    class Meta:
        model = AssignedAppointment
        fields = ['appointment', 'assigned_machine', 'assigned_provider']

    #transforming data into array of object
    def get_assigned_provider(self, obj):
        providers = obj.assigned_provider or []
        return [{"provider": p} for p in providers]
    
    #transforming data into array of object
    def get_assigned_machine(self, obj):
        #access the related AssignedMachine and return its real value
        machine_value = getattr(obj.assigned_machine, 'assigned_machine', None) #actual value of the machine
        return [{"machine": m} for m in machine_value]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        #remove the appointment_id
        data.pop('appointment')
        #return the updated data
        return data 

class GetAppointmentsInProviderSerializer(serializers.ModelSerializer):

    appointments = GetAssignedAppointmentInProviderSerializer()
    formatted_date_time = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    class Meta:
        model = Appointment
        fields = ['patient_name', 'formatted_date_time', 'status', 'appointments']

    def get_formatted_date_time(self, obj):

        date_time = obj.date_time
        if date_time:
            return date_time.strftime("%b %d, %Y - %I:%M %p")
        return None
    
    def get_patient_name(self, obj):
        firstname_value = getattr(obj.user, 'first_name', None)
        lastname_value = getattr(obj.user, 'last_name', None)

        if firstname_value and lastname_value:
            return f"{firstname_value} {lastname_value}"
        return None


