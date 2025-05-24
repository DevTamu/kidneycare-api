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
    
    def validate(self, attrs):

        time = attrs.get('time', None)
    #     date = attrs.get('date', None)

        schedule_data = Schedule.objects.get(id=1)

        #convert time into datetime objects
        start_time = datetime.strptime(schedule_data.start_time.strftime('%I:%M %p'), '%I:%M %p')
        end_time = datetime.strptime(schedule_data.end_time.strftime('%I:%M %p'), '%I:%M %p')

        #generate interval every 1 hour
        interval = timedelta(hours=1)
        current_time = start_time

        #store all the available time in 'time slots'
        time_slots = []

        while current_time <= end_time:
            #append the current_time to time slots
            time_slots.append(current_time)
            #adding 1hr interval to the current_time
            current_time += interval


        #format the time to 12-hour strings
        formatted_time_slots = [datetime.strftime(slot, '%I:%M:%S') for slot in time_slots]

        #format the input time to readable format
        formatted_time_input = time.strftime('%I:%M:%S')

        #if the time slots not exist
        if formatted_time_input not in formatted_time_slots:
            raise serializers.ValidationError({"message": "This time is not available"})
        
        #check for every taken slots
        #taken_slots = [time_slot for time_slot in formatted_time_slots if Appointment.objects.filter(time=time_slot).exists()]

    #     #check if the slots already in taken slots means someone already booked that time
    #     if formatted_time_input in taken_slots and date == schedule_data.date_created:
    #         raise serializers.ValidationError({"message": "This time slot is already booked. Please choose different time."})


        return attrs
    
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
    

    def validate(self, attrs):

        time = attrs.get('time', None)
        # date = attrs.get('date', None)

        schedule_data = Schedule.objects.get(id=1)

        #convert time into datetime objects
        start_time = datetime.strptime(schedule_data.start_time.strftime('%I:%M %p'), '%I:%M %p')
        end_time = datetime.strptime(schedule_data.end_time.strftime('%I:%M %p'), '%I:%M %p')

        #generate interval every 1 hour
        interval = timedelta(hours=1)
        current_time = start_time

        #store all the available time in 'time slots'
        time_slots = []

        while current_time <= end_time:
            #append the current_time to time slots
            time_slots.append(current_time)
            #adding 1hr interval to the current_time
            current_time += interval


        #format the time to 12-hour strings
        formatted_time_slots = [datetime.strftime(slot, '%I:%M:%S') for slot in time_slots]

        #format the input time to readable format
        formatted_time_input = time.strftime('%I:%M:%S')

        #if the time slots not exist
        if formatted_time_input not in formatted_time_slots:
            raise serializers.ValidationError({"message": "This time is not available"})
        

        return attrs    
        #check for every taken slots
        #taken_slots = [time_slot for time_slot in formatted_time_slots if Appointment.objects.filter(time=time_slot).exists()]

    #     #check if the slots already in taken slots means someone already booked that time
    #     if formatted_time_input in taken_slots and date == schedule_data.date_created:
    #         raise serializers.ValidationError({"message": "This time slot is already booked. Please choose different time."})
    
    #update date and time of the patient appointment (for reschedule)
    def update(self, instance, validated_data):
        
        instance.date = validated_data["date"]
        instance.time = validated_data["time"]

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
    
    assigned_machine = AddAssignedMachineSerializer()
    assigned_provider = AddAssignedProviderSerializer()
    status = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta:
        model = AssignedAppointment
        fields = ['assigned_provider', 'assigned_machine', 'status']

    def validate(self, attrs):
        
        #extract the assigned machine data
        assigned_machine_data = attrs.get('assigned_machine', [])

        #extract the assigned provider data
        assigned_provider_data = attrs.get('assigned_provider', [])

        if is_field_empty(attrs.get('status')):
            raise serializers.ValidationError({"message": "Status is required"})

        if is_field_empty(assigned_machine_data):
            raise serializers.ValidationError({"message": "Please assign a machine"})
        
        if is_field_empty(assigned_provider_data):
            raise serializers.ValidationError({"message": "Please assign a provider"})

        return attrs
    

    #create assigned appointments along with their machines and providers.
    #uses an atomic transaction to ensure rollback in case of any failure.
    @transaction.atomic
    def create(self, validated_data):

        #extract the assigned machine data
        assigned_machines_data = validated_data.pop('assigned_machine')

        #extract the assigned provider data
        assigned_providers_data = validated_data.pop('assigned_provider')

        appointment = self.context.get('appointment_pk')

        #create assigned machine object instance linked to the appointment
        assigned_machine_obj = AssignedMachine.objects.create(
            assigned_machine_appointment=appointment,
            assigned_machine=assigned_machines_data["assigned_machine"],
            status='In use'
        )

        #create assigned provider object instance linked to the appointment
        assigned_provider_obj = AssignedProvider.objects.create(
            assigned_provider=assigned_providers_data["assigned_provider"],
            assigned_patient_appointment=appointment
        )

        #create assigned appointment object instance linked to the appointment
        assigned_appointment_obj = AssignedAppointment.objects.create(
            appointment=appointment,
            assigned_machine=assigned_machine_obj,
            assigned_provider=assigned_provider_obj
        )

        Appointment.objects.update_or_create(
            id=appointment.id,
            defaults={
                "status": validated_data.get('status', None)
            }
        )

        return assigned_appointment_obj

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
    assigned_provider = GetAssignedProviderSerializer()
    assigned_machine = GetAssignedMachineSerializer()

    class Meta:
        model = AssignedAppointment
        fields = ['assigned_machine', 'assigned_provider']


    def to_representation(self, instance):
        data = super().to_representation(instance)

        #flatten the response by extracting 'assigned_provider' and 'assigned_machine'
        assigned_provider = data.pop('assigned_provider', {})
        assigned_machine = data.pop('assigned_machine', {})

        #merge 'assigned_provider' and 'assigned_machine' into the main data dictionary
        data.update(assigned_machine)
        data.update(assigned_provider)

        return data


#DONE
class GetAppointmentsInProviderSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    machine = serializers.SerializerMethodField()
    provider = serializers.SerializerMethodField()

    class Meta:
        model = AssignedAppointment
        fields = ['first_name', 'last_name', 'user_id', 'date', 'time', 'machine', 'provider']


    def to_representation(self, instance):

        #get the request from the serializer context
        request = self.context.get('request')

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        user_id = data.get('user_id')


        try:
            user_profile = Profile.objects.get(user=user_id)
        except Exception as e:
            user_profile = None

        data["user_image"] = request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None

        return data
    
    #get the assigned provider of the patient from the related appointment
    def get_provider(self, obj):
        return str(obj.assigned_provider.assigned_provider)
    
    #get the assigned machine of the patient from the related appointment
    def get_machine(self, obj):
        return int(obj.assigned_machine.assigned_machine)
    
    #get the firstname of the patient from the related appointment
    def get_first_name(self, obj):
        return obj.appointment.user.first_name

    #get the lastname of the patient from the related appointment
    def get_last_name(self, obj):
        return obj.appointment.user.last_name

    #get the id of the patient from the related appointment
    def get_user_id(self, obj):
        return str(obj.appointment.user.id)
       
    #format the appointment date in a readable format (e.g., May 25, 2025
    def get_date(self, obj):
        return obj.appointment.date.strftime('%B %d, %Y')

    #format the appointment time in a readable format (e.g., May 25, 2025
    def get_time(self, obj):
        return obj.appointment.time.strftime('%I:%M %p')
    
    

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
        
        #remove id from the response
        data.pop('id')

        data["patient_name"] = f'{data.pop('first_name').capitalize()} {data.pop('last_name').capitalize()}'
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

        assigned_provider = None

        #remove the user, id from the response
        user_id = data.pop('user')
        appointment_id = data.pop('id')

        data["user_id"] = str(user_id).replace("-", "")
        data["appointment_id"] = appointment_id

        #fetch all assigned appointments linked to the specific appointment
        #and get the related assigned machine, provider
        try:
            assigned_appointments = AssignedAppointment.objects  \
            .prefetch_related('assigned_machine', 'assigned_provider')  \
            .filter(appointment=appointment_id).first()
        except AssignedAppointment.DoesNotExist:
            pass

        if assigned_appointments and assigned_appointments.assigned_provider.assigned_provider:
            assigned_provider = assigned_appointments.assigned_provider.assigned_provider
            data["first_name"] = assigned_appointments.assigned_provider.assigned_provider.first_name
            data["last_name"] = assigned_appointments.assigned_provider.assigned_provider.last_name
            data["role"] = assigned_appointments.assigned_provider.assigned_provider.role
        else:
            data["first_name"] = None
            data["last_name"] = None
            data["role"] = None
       
        if assigned_provider:

            try:
                user_profile = Profile.objects.filter(user=assigned_provider).first()
            except Profile.DoesNotExist:
                pass

        #add profile picture URL (absolute URI) to the response if available
        data["user_image"] = (
            request.build_absolute_uri(user_profile.picture.url)
            if user_profile.picture else None
        )


        return data


class GetPendingAppointsmentsInAdminSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    picture = serializers.SerializerMethodField()
    assigned_provider = serializers.SerializerMethodField()
    assigned_machine = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'first_name', 'last_name', 'date', 'time', 'status', 'picture', 'user', 'assigned_provider', 'assigned_machine']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        #rename key
        data["appointment_id"] = data.pop('id')
        data["user_id"] = str(data.pop('user')).replace("-", "")

        return data

    def get_first_name(self, obj):
        return str(obj.user.first_name)
    
    def get_last_name(self, obj):
        return str(obj.user.last_name)
    
    def get_date(self, obj):
        return obj.date.strftime('%b %d, %Y')
    
    def get_time(self, obj):
        return obj.time.strftime('%I:%M %p')
    
    def get_status(self, obj):
        return str(obj.status)
    
    def get_picture(self, obj):

        request = self.context.get('request')

        user_profile = Profile.objects.get(user=obj.user)

        return request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None
    
    def get_assigned_provider(self, obj):

        assigned_provider = AssignedAppointment.objects.select_related('appointment').filter(appointment=obj)

        for provider in assigned_provider:

            if provider and provider.assigned_provider:
                return f'{provider.assigned_provider.assigned_provider.first_name} {provider.assigned_provider.assigned_provider.last_name}'
            return None
        
    def get_assigned_machine(self, obj):

        assigned_machine = AssignedAppointment.objects.select_related('appointment').filter(appointment=obj)

        for machine in assigned_machine:

            if machine and machine.assigned_machine:
                return int(machine.assigned_machine.assigned_machine)
            return None




class CancelAppointmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CancelAppointmentSerializer, self).__init__(*args, **kwargs)
        #make all the fields not required
        for field in self.fields.values():
            field.required = False


class GetPatientUpcomingAppointmentsSerializer(serializers.ModelSerializer):

    date = serializers.DateField(format='%m/%d/%Y', input_formats=['%m/%d/%Y'])
    time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])
    
    
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'user', 'id']

    def to_representation(self, instance):
        
        #initialize these variable to None
        assigned_machine_upcoming_appointment = None
        assigned_provider_upcoming_appointment = None
        provider_profile = None
        provider = None

        #get the request object from the serializer context
        request = self.context.get('request')

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        #rename keys
        data["user_id"] = str(data.pop('user')).replace("-", "")
        data["appointment_id"] = data.pop('id')

        #get the assigned machined to the related appointment of the patient upcoming appointment
        try:
            assigned_machine_upcoming_appointment = AssignedMachine.objects.filter(
                assigned_machine_appointment=data.get('appointment_id', None)
            ).first()
        except AssignedMachine.DoesNotExist:
            pass

        #safe access to machine data
        if assigned_machine_upcoming_appointment and assigned_machine_upcoming_appointment.assigned_machine:
            data["machine"] = f'Machine #{assigned_machine_upcoming_appointment.assigned_machine}'
        else:
            data["machine"] = None

        #get the assigned provider to the related appointment of the patient upcoming appointment
        try:
            assigned_provider_upcoming_appointment = AssignedProvider.objects.filter(
                assigned_patient_appointment=data.get('appointment_id', None)
            ).first()
        except AssignedProvider.DoesNotExist:
            pass
        
        #safe access to provider data
        if assigned_provider_upcoming_appointment and assigned_provider_upcoming_appointment.assigned_provider:
            provider = assigned_provider_upcoming_appointment.assigned_provider
            data["assigned_provider_name"] = f'{provider.role.capitalize()} {provider.first_name.capitalize()}'
        else:
            data["assigned_provider_name"] = None


        if provider:
            try:
                provider_profile = Profile.objects.filter(user=provider.id).first()
            except Profile.DoesNotExist:
                provider_profile = None


        if provider_profile and provider_profile.picture:
            data["picture"] = request.build_absolute_uri(provider_profile.picture.url)
        else:
            data["picture"] = None


        return data

class GetPatientUpcomingAppointmentSerializer(serializers.ModelSerializer):

    date = serializers.DateField(format='%m/%d/%Y', input_formats=['%m/%d/%Y'])
    time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])
    
    
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'user', 'id']

    def to_representation(self, instance):
        
        #initialize these variable to None
        assigned_machine_upcoming_appointment = None
        assigned_provider_upcoming_appointment = None
        provider_profile = None
        provider = None

        #get the request object from the serializer context
        request = self.context.get('request')

        #get the default serialized data from the parent class
        data = super().to_representation(instance)

        #rename keys
        data["user_id"] = str(data.pop('user')).replace("-", "")
        data["appointment_id"] = data.pop('id')

        #get the assigned machined to the related appointment of the patient upcoming appointment
        try:
            assigned_machine_upcoming_appointment = AssignedMachine.objects.filter(
                assigned_machine_appointment=data.get('appointment_id', None)
            ).first()
        except AssignedMachine.DoesNotExist:
            pass

        #safe access to machine data
        if assigned_machine_upcoming_appointment and assigned_machine_upcoming_appointment.assigned_machine:
            data["machine"] = f'Machine #{assigned_machine_upcoming_appointment.assigned_machine}'
        else:
            data["machine"] = None

        #get the assigned provider to the related appointment of the patient upcoming appointment
        try:
            assigned_provider_upcoming_appointment = AssignedProvider.objects.filter(
                assigned_patient_appointment=data.get('appointment_id', None)
            ).first()
        except AssignedProvider.DoesNotExist:
            pass
        
        #safe access to provider data
        if assigned_provider_upcoming_appointment and assigned_provider_upcoming_appointment.assigned_provider:
            provider = assigned_provider_upcoming_appointment.assigned_provider
            data["assigned_provider_name"] = f'{provider.role.capitalize()} {provider.first_name.capitalize()}'
        else:
            data["assigned_provider_name"] = None

        if provider:
            #get the provider's profile safely
            try:
                provider_profile = Profile.objects.filter(user=provider.id).first()
            except Profile.DoesNotExist:
                pass

        if provider_profile and provider_profile.picture:
            data["picture"] = request.build_absolute_uri(provider_profile.picture.url)
        else:
            data["picture"] = None


        return data
    

class GetPatientAppointmentDetailsInAdminSerializer(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id','first_name', 'last_name', 'status', 'date_time', 'user_image', 'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["appointment_id"] = data.pop('id')

        data["user_id"] = str(data.pop('user')).replace("-", "")

        return data

    def get_user_image(self, obj):

        user_profile = Profile.objects.get(user=obj.user)

        #get the request object from the serializer context
        request = self.context.get('request')

        return request.build_absolute_uri(user_profile.picture.url) if user_profile.picture else None
    
    def get_date_time(self, obj):
        return f'{obj.date.strftime('%b %d, %Y')} - {obj.time.strftime('%I:%M %p')}'

    def get_first_name(self, obj):
        return obj.user.first_name
    
    def get_last_name(self, obj):
        return obj.user.last_name
        
    def get_status(self, obj):
        return obj.status


class CancelPatientUpcomingAppointmentInAppointmentPageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Appointment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CancelAppointmentSerializer, self).__init__(*args, **kwargs)
        #make all the fields not required
        for field in self.fields.values():
            field.required = False





