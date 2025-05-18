from rest_framework import serializers
from .models import Appointment, AssignedAppointment, AssignedMachine, AssignedProvider
from kidney.utils import is_field_empty
from django.db import transaction
import logging
from app_authentication.models import User, Profile, UserInformation
from app_schedule.models import Schedule 
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CreateAppointmentSerializer(serializers.ModelSerializer):

    date = serializers.DateField(format='%m/%d/%Y',input_formats=['%m/%d/%Y'])
    time = serializers.TimeField(format='%I:%M %p',input_formats=['%I:%M %p'])

    class Meta:
        model = Appointment
        fields = ['time', 'date']

    def to_internal_value(self, data):
        
        if data["date"] in (None, ""):
            raise serializers.ValidationError({"message": "Date is required to book an appointment"})

        if data["time"] in (None, ""):
            raise serializers.ValidationError({"message": "Time is required to book an appointment"})
        
        return super().to_internal_value(data)
    
    # def validate(self, attrs):

    #     time = attrs.get('time', None)
    #     date = attrs.get('date', None)

    #     schedule_data = Schedule.objects.get(id=3)

    #     #convert time into datetime objects
    #     start_time = datetime.strptime(schedule_data.start_time.strftime('%I:%M %p'), '%I:%M %p')
    #     end_time = datetime.strptime(schedule_data.end_time.strftime('%I:%M %p'), '%I:%M %p')

    #     #generate interval every 1 hour
    #     interval = timedelta(hours=1)
    #     current_time = start_time

    #     time_slots = []

    #     while current_time <= end_time:
    #         #append the current_time to time slots
    #         time_slots.append(current_time)
    #         #adding 1hr interval to the current_time
    #         current_time += interval


    #     #format the time to 12-hour strings
    #     formatted_time_slots = [datetime.strftime(slot, '%I:%M:%S') for slot in time_slots]

    #     #format the input time to readable format
    #     formatted_time_input = time.strftime('%I:%M:%S')

    #     #if the time slots not exist
    #     if formatted_time_input not in formatted_time_slots:
    #         raise serializers.ValidationError({"message": "This time is not available"})
        
    #     #check for every taken slots
    #     taken_slots = [time_slot for time_slot in formatted_time_slots if Appointment.objects.filter(time=time_slot).exists()]

    #     #check if the slots already in taken slots means someone already booked that time
    #     if formatted_time_input in taken_slots and date == schedule_data.date_created:
    #         raise serializers.ValidationError({"message": "This time slot is already booked. Please choose different time."})


    #     return attrs
    
    def create(self, validated_data):

        #get the request object from the serializer context
        request = self.context.get('request')

        #create an appointment linked to the current authenticated user/patient
        create_appointment = Appointment.objects.create(
            user=request.user,
            date=validated_data.get('date', None),
            time=validated_data.get('time', None).strftime('%I:%M:%S'),
        )

        #return the created appointment
        return create_appointment


class UpdateAppointmentInPatientSerializer(serializers.ModelSerializer):

    #format the date and time to readable format
    date = serializers.DateField(format='%m/%d/%Y',input_formats=['%m/%d/%Y'])
    time = serializers.TimeField(format='%H:%M %p',input_formats=['%H:%M %p'], allow_null=True)

    class Meta:
        model = Appointment
        fields = ['id','date', 'time']

    #date and time validation
    def to_internal_value(self, data):
        if data['date'] in (None, ""):
            raise serializers.ValidationError({"message": "Date is required"})
        
        if data["time"] in (None, ""):
            raise serializers.ValidationError({"message": "Time is required"})
        
        return super().to_internal_value(data)
    
    #update date and time of the patient appointment (for reschedule)
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
    

    #create assigned appointments along with their machines and providers.
    #uses an atomic transaction to ensure rollback in case of any failure.
    @transaction.atomic
    def create(self, validated_data):

        #extract the assigned machine data
        assigned_machines_data = validated_data.pop('assigned_machines')

        #extract the assigned provider data
        assigned_providers_data = validated_data.pop('assigned_providers')

        appointment = validated_data['appointment']
        #create a new AssignedAppointment instance linked to the appointment
        assigned_appointment = AssignedAppointment.objects.create(appointment=appointment)

        #loop through each machine to create or get the AssignedMachine, then link it to the appointment
        for machine_data in assigned_machines_data:
            machine_obj, _ = AssignedMachine.objects.get_or_create(
                assigned_machine_appointment=appointment,
                assigned_machine=machine_data['assigned_machine'],
                status=machine_data['status']
            )
            assigned_appointment.assigned_machines.add(machine_obj)
            
        #loop through each provider to create or get the AssignedProvider
        for provider_data in assigned_providers_data:
            provider_obj, _ = AssignedProvider.objects.get_or_create(
                assigned_provider=provider_data['assigned_provider'],
                assigned_provider_appointments=appointment
            )
            assigned_appointment.assigned_providers.add(provider_obj)

        #return the created assigned appointment
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
        return f"{user.first_name} {user.last_name}" if user else None



class GetAssignedAppointmentSerializer(serializers.ModelSerializer):
    assigned_providers = GetAssignedProviderSerializer(many=True)
    assigned_machines = GetAssignedMachineSerializer(many=True)

    class Meta:
        model = AssignedAppointment
        fields = ['assigned_machines', 'assigned_providers']


#DONE
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

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        #rename keys
        data["patient_name"] = f'{data.pop('first_name')} {data.pop('last_name')}'
        data["appointment_date_time"] = f'{data.pop('date')} - {data.pop('time')}'

        data["assigned_appointments"] = data.pop('assigned_appointments')

        return data
    
    #transforming date to readable format
    def get_date(self, obj):

        date = obj.date
        if date:
            return date.strftime("%b %d, %Y")
        return None
    
    #transforming time to readable format
    def get_time(self, obj):

        time = obj.time
        if time:
            return time.strftime("%I:%M %p")
        return None
    
    #get the actual first name value from the related user object
    def get_first_name(self, obj):
        firstname_value = getattr(obj.user, 'first_name')
        return firstname_value
    
    #get the actual last name value from the related user object
    def get_last_name(self, obj):

        lastname_value = getattr(obj.user, 'last_name')
        return lastname_value
    
    #get the actual user id value from the related user object
    def get_user_id(self, obj):

        user_id = getattr(obj.user, 'id')
        return user_id
    
    

class GetPatientInformationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'id']

    def to_representation(self, instance):

        #get the request object from the serializer context
        request = self.context.get('request')

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        #get the user information based on the id
        user_information = UserInformation.objects.get(user=data.get('id'))

        if not user_information:
            raise serializers.ValidationError({"message": "User information not found"})

        #get the user profile based on the id
        user_profile = Profile.objects.get(user=data.get('id'))

        if not user_profile:
            raise serializers.ValidationError({"message": "User profile not found"})
        
        data["patient_name"] = f'{data.pop('first_name')} {data.pop('last_name')}'
        data["patient_age"] = user_information.age
        data["patient_birth_date"] = user_information.birthdate
        data["patient_contact_number"] = user_information.contact
        data["patient_gender"] = user_information.gender
        data["patient_profile"] = request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None
        
        return data
    

class GetPatientAppointmentHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = ['user', 'status', 'id']


    def to_representation(self, instance):
        
        #get the request object from the serializer context
        request = self.context.get('request')

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        appointment_id = data.get('id')
        
        #fetch all assigned appointments linked to this appointment
        assigned_appointments = AssignedAppointment.objects.filter(appointment=appointment_id)

        #loop through of all the assigned appointments
        for assigned_appointment in assigned_appointments:
            #get all providers assigned to the current appointment
            assigned_providers = assigned_appointment.assigned_providers.all()

            #loop through each assigned provider
            for provider in assigned_providers:
                #access the actual provider object from the assigned provider relation
                assigned_provider = provider.assigned_provider

                #check if the provider exists and has a role
                if assigned_provider and assigned_provider.role:
                    #add provider details to the serialized output
                    data["role"] = assigned_provider.role
                    data["provider_first_name"] = assigned_provider.first_name
                    data["provider_last_name"] = assigned_provider.last_name

                #retrieve the user's profile
                user_profile = Profile.objects.get(user=assigned_provider.id)

                #add profile picture URL (absolute URI) to the response if available
                data["user_profile"] = (
                    request.build_absolute_uri(user_profile.picture.url)
                    if user_profile.picture else None
                )

        #rename keys
        data["user_id"] = data.pop('user')
        data["appointment_id"] = data.pop('id')

        return data


class GetPendingAppointsmentsInAdminSerializer(serializers.ModelSerializer):

    #format the date and time to readable format
    date = serializers.DateField(format='%b %d, %Y', input_formats=['%b %d, %Y'])
    time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])

    class Meta:
        model = Appointment
        fields = ['user', 'date', 'time', 'status']

    def to_representation(self, instance):

        #get the request object from the serializer context
        request = self.context.get('request')

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        #foreign key user id
        user_id = data.get('user')

        #get the matched users of the foreign key user id
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"message": "User not found"})
        
        #get the matched user profiles of the foreign key user id
        try:
            user_profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise serializers.ValidationError({"message": "User profile not found"})
        
        #rename keys
        data["patient_first_name"] = user.first_name
        data["patient_last_name"] = user.last_name

        #add profile picture URL (absolute URI) to the response if available
        data["patient_profile"] = (
            request.build_absolute_uri(user_profile.picture.url)
            if user_profile.picture else None
        )


        return data
    

class CancelAppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CancelAppointmentSerializer, self).__init__(*args, **kwargs)
        #make all the fields not required
        for field in self.fields.values():
            field.required = False


class GetPatietnUpcomingAppointmentSerializer(serializers.ModelSerializer):

    date = serializers.DateField(format='%m/%d/%Y', input_formats=['%m/%d/%Y'])
    time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])
    
    
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'user', 'id']

    def to_representation(self, instance):

        #get the request object from the serializer context
        request = self.context.get('request')

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        data["user_id"] = str(data.pop('user')).replace("-", "")

        #get the assigned machined to the related appointment of the patient upcoming appointment
        assigned_machine_upcoming_appointment = AssignedMachine.objects.get(
            assigned_machine_appointment=data.get('id', None)
        )

        #get the assigned provider to the related appointment of the patient upcoming appointment
        assigned_provider_upcoming_appointment = AssignedProvider.objects.get(
            assigned_provider_appointments=data.get('id', None)
        )

        data["machine"] = f'Machine #{assigned_machine_upcoming_appointment.assigned_machine}'

        data["name"] = f'{assigned_provider_upcoming_appointment.assigned_provider.role.capitalize()} {assigned_provider_upcoming_appointment.assigned_provider.first_name.capitalize()}'

        #get the profile of the assigned provider
        provider_profile = Profile.objects.get(user=assigned_provider_upcoming_appointment.assigned_provider.id)

        data["picture"] = request.build_absolute_uri(provider_profile.picture.url) if provider_profile.picture else None

        return data





