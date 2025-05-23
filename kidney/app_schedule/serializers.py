from rest_framework import serializers
from .models import Schedule
from kidney.utils import is_field_empty
from .models import Schedule
from datetime import datetime, timedelta
from django.utils import timezone


class CreateScheduleSerializer(serializers.ModelSerializer):
    
    available_days = serializers.ListField(
        child=serializers.CharField()
    )
    start_time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])
    end_time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])

    class Meta:
        model = Schedule
        fields = ['available_days', 'start_time', 'end_time']


    def validate(self, attrs):
        
        required_fields = ['available_days', 'start_time', 'end_time']

        for field in required_fields:
            if is_field_empty(attrs.get(field)):
                raise serializers.ValidationError({"message": "All fields are required to create an schedule"})

        return attrs

    def create(self, validated_data):

        return Schedule.objects.update_or_create(
            id=3,
            defaults={
                "available_days": validated_data.get('available_days', []),
                "start_time": validated_data.get('start_time', None),
                "end_time": validated_data.get('end_time', None),
                "date_created": timezone.now,
            }
        )
    

class GetScheduleSerializer(serializers.ModelSerializer):
    
    start_time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])
    end_time = serializers.TimeField(format='%I:%M %p', input_formats=['%I:%M %p'])

    class Meta:
        model = Schedule
        fields = '__all__'


    def to_representation(self, instance):
        data = super().to_representation(instance)

        #removed from the response
        data.pop('created_at')
        data.pop('updated_at')
        data.pop('date_created')
        data.pop('id')

        #convert to datetime objects
        schedule_start_time = datetime.strptime(data.pop('start_time'), '%I:%M %p')
        schedule_end_time = datetime.strptime(data.pop('end_time'), '%I:%M %p')

        #generate time interval every hour
        interval = timedelta(hours=1)
        #starting time of our schedule
        current_time = schedule_start_time

        #slots for scheduled time
        time_slots = [] 

        while current_time <= schedule_end_time:
            #add the current_time to time slots
            time_slots.append(current_time)
            #adding 1hr interval to the current_time
            current_time += interval

        #sort by datetime before formatting
        time_slots.sort()

        #format the time to 12-hour strings
        formatted_slots = [slot.strftime("%I:%M %p") for slot in time_slots]

        data["available_time"] = formatted_slots

        return data