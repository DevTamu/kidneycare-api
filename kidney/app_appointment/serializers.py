from rest_framework import serializers
from rest_framework import status
from .models import Appointment, AssignedAppointment, AssignedMachine, AssignedProvider
from kidney.utils import is_field_empty
from django.db import transaction
import logging
from app_authentication.models import User
from django.db.models import Q
from kidney.utils import ucfirst
from datetime import datetime

logger = logging.getLogger(__name__)


# class CreateAssignedAppointmentSerializer(serializers.Serializer):
#     assigned_provider = serializers.ListField(
#         child=serializers.CharField(), allow_empty=False
#     )
#     assigned_machine = serializers.ListField(
#         child=serializers.CharField(), allow_empty=False
#     )


class CreateAppointmentSerializer(serializers.ModelSerializer):

    date = serializers.DateField(format='%m/%d/%Y',input_formats=['%m/%d/%Y'])
    time = serializers.TimeField(format='%H:%M %p',input_formats=['%H:%M %p'], allow_null=True)

    class Meta:
        model = Appointment
        fields = ['date', 'time']


    def to_internal_value(self, data):
        if data['date'] in (None, ""):
            raise serializers.ValidationError({"message": "Date is required"})
        
        if data["time"] in (None, ""):
            raise serializers.ValidationError({"message": "Time is required"})
        
        return super().to_internal_value(data)

    
    def create(self, validated_data):

        #get the request from the context
        request = self.context.get('request')

        appointment = Appointment.objects.create(
            user=request.user,
            date=validated_data.get('date', None),
            time=validated_data.get('time', None),
        )

        return appointment


class UpdateAppointmentInPatientSerializer(serializers.ModelSerializer):

    date = serializers.DateField(format='%m/%d/%Y',input_formats=['%m/%d/%Y'])
    time = serializers.TimeField(format='%H:%M %p',input_formats=['%H:%M %p'], allow_null=True)

    class Meta:
        model = Appointment
        fields = ['id','date', 'time']

    def to_internal_value(self, data):
        if data['date'] in (None, ""):
            raise serializers.ValidationError({"message": "Date is required"})
        
        if data["time"] in (None, ""):
            raise serializers.ValidationError({"message": "Time is required"})
        
        return super().to_internal_value(data)
        
    def update(self, instance, validated_data):
        
        instance.date = validated_data.get('date', None)
        instance.time = validated_data.get('time', None)

        instance.save()

        return instance


class AddAssignedMachineSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignedMachine
        fields = ['assigned_machine', 'status']


class AddAssignedProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignedProvider
        fields = ['assigned_provider']

class AddAppointmentDetailsInAdminSerializer(serializers.Serializer):
    
    assigned_machines = AddAssignedMachineSerializer(many=True)
    assigned_providers = AddAssignedProviderSerializer(many=True)

    class Meta:
        model = AssignedAppointment
        fields = ['appointment', 'assigned_providers', 'assigned_machines']

    def validate(self, attrs):
        
        #extract the assigned machine data
        assigned_machine_data = attrs.get('assigned_machines', [])

        #extract the assigned provider data
        assigned_provider_data = attrs.get('assigned_providers', [])

        if is_field_empty(assigned_machine_data):
            raise serializers.ValidationError({"message": "Assign a machine"})
        
        if is_field_empty(assigned_provider_data):
            raise serializers.ValidationError({"message": "Assign a provider"})

        return attrs
        

    def create(self, validated_data):

        #extract the assigned machine data
        assigned_machines_data = validated_data.pop('assigned_machines')

        #extract the assigned provider data
        assigned_providers_data = validated_data.pop('assigned_providers')

        appointment = validated_data['appointment']
        assigned_appointment = AssignedAppointment.objects.create(appointment=appointment)
        
        for machine_data in assigned_machines_data:
            machine_obj, _ = AssignedMachine.objects.get_or_create(
                assigned_machine=machine_data['assigned_machine'],
                status=machine_data['status']
            )
            assigned_appointment.assigned_machines.add(machine_obj)
            

        for provider_data in assigned_providers_data:
            provider_obj, _ = AssignedProvider.objects.get_or_create(
                assigned_provider=provider_data['assigned_provider']
            )
            assigned_appointment.assigned_providers.add(provider_obj)

        return assigned_appointment

class GetAssignedMachineSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AssignedMachine
        fields = ['assigned_machine']

class GetAssignedProviderSerializer(serializers.ModelSerializer):

    assigned_provider = serializers.SerializerMethodField()

    class Meta:
        model = AssignedProvider
        fields = ['assigned_provider']

    def get_assigned_provider(self, obj):
        user = obj.assigned_provider 
        return f"{user.first_name} {user.last_name}" if user else "Unknown User"



class GetAssignedAppointmentSerializer(serializers.ModelSerializer):
    assigned_providers = GetAssignedProviderSerializer(many=True)
    assigned_machines = GetAssignedMachineSerializer(many=True)

    class Meta:
        model = AssignedAppointment
        fields = ['assigned_machines', 'assigned_providers']
        # fields = ['appointment', 'assigned_machines', 'assigned_providers']

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)

    #     #rename key of the appointment id
    #     data["appointment_id"] = data.pop('appointment')

    #     return data


class GetAppointmentsInProviderSerializer(serializers.ModelSerializer):

    assigned_appointments = GetAssignedAppointmentSerializer(many=True)
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['first_name', 'last_name', 'user_id', 'date', 'time', 'status', 'assigned_appointments']


    def to_representation(self, instance):

        data = super().to_representation(instance)

        data["patient_name"] = f'{data.pop('first_name')} {data.pop('last_name')}'
        data["appointment_date_time"] = f'{data.pop('date')} - {data.pop('time')}'

        data["assigned_appointments"] = data.pop('assigned_appointments')

        return data

    def get_date(self, obj):

        date = obj.date
        if date:
            return date.strftime("%b %d, %Y")
        return None
    
    def get_time(self, obj):

        time = obj.time
        if time:
            return time.strftime("%I:%M %p")
        return None
    
    def get_first_name(self, obj):

        firstname_value = getattr(obj.user, 'first_name')
        return firstname_value
    
    def get_last_name(self, obj):

        lastname_value = getattr(obj.user, 'last_name')
        return lastname_value
    
    def get_user_id(self, obj):

        user_id = getattr(obj.user, 'id')
        return user_id
    
    


class GetAppointmentDetailsInProviderSerializer(serializers.ModelSerializer):

    assigned_appointments = GetAssignedAppointmentSerializer()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['patient_name', 'user', 'date', 'time', 'status', 'assigned_appointments']

    def to_representation(self, instance):

    #     #get the request from the context
    #     request = self.context.get('request')

        data = super().to_representation(instance)

        user_id = data.pop('user')

        data["user_id"] = user_id

    #     # get the fullname of the current user logged in assuming its (Provider)
    #     full_name = f"{request.user.first_name} {request.user.last_name}"

    #     #get all the assigned appointments data
    #     matching_assigned_appointments = AssignedAppointment.objects.all()

    #     #store all the appointment id here
    #     matched_appointments_ids = []

    #     #loop through of all the matching assigned appointments
    #     for assigned in matching_assigned_appointments:
    #         provider_list = assigned.assigned_provider or []
    #         if full_name in provider_list and assigned.appointment.status == 'Approved':
    #             matched_appointments_ids.append(assigned.appointment.id)

    #     #if there is matched id return all the data
    #     if instance.id in matched_appointments_ids:
    #         return data
    #     else:
    #         return {}

        return data


    def get_date(self, obj):

        date = obj.date
        if date:
            return date.strftime("%b/%d/%Y")
        return None
    
    def get_time(self, obj):

        time = obj.time
        if time:
            return time.strftime("%H:%M %p")
        return None
    
    def get_patient_name(self, obj):
        firstname_value = getattr(obj.user, 'first_name', None)
        lastname_value = getattr(obj.user, 'last_name', None)

        if firstname_value and lastname_value:
            return f"{ucfirst(firstname_value)} {ucfirst(lastname_value)}"
        return None
    

# class GetAppointmentsInAdminSerializer(serializers.ModelSerializer):

#     appointments = GetAssignedAppointmentSerializer()
#     date_time = serializers.SerializerMethodField()
#     patient_name = serializers.SerializerMethodField()

#     class Meta:
#         model = Appointment
#         fields = ['patient_name', 'date_time', 'status', 'appointments']

#     # def to_representation(self, instance):

#     #     #get the request from the context
#     #     request = self.context.get('request')

#     #     data = super(GetAppointmentsInProviderSerializer, self).to_representation(instance)

#     #     # get the fullname of the current user logged in assuming its (Provider)
#     #     full_name = f"{request.user.first_name} {request.user.last_name}"

#     #     #get all the assigned appointments data
#     #     matching_assigned_appointments = AssignedAppointment.objects.all()

#     #     #store all the appointment id here
#     #     matched_appointments_ids = []

#     #     #loop through of all the matching assigned appointments
#     #     for assigned in matching_assigned_appointments:
#     #         provider_list = assigned.assigned_provider or []
#     #         if full_name in provider_list and assigned.appointment.status == 'Pending':
#     #             matched_appointments_ids.append(assigned.appointment.id)

#     #     #if there is matched id return all the data
#     #     if instance.id in matched_appointments_ids:
#     #         return data
#     #     else:
#     #         return {}


#     def get_date_time(self, obj):

#         date_time = obj.date_time
#         if date_time:
#             return date_time.strftime("%b %d, %Y - %I:%M %p")
#         return None
    
#     def get_patient_name(self, obj):
#         firstname_value = getattr(obj.user, 'first_name', None)
#         lastname_value = getattr(obj.user, 'last_name', None)

#         if firstname_value and lastname_value:
#             return f"{ucfirst(firstname_value)} {ucfirst(lastname_value)}"
#         return None


