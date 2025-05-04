import datetime
from rest_framework import serializers
from .models import NewsEvent, NewsEventImage
from django.db import transaction


class AddNewsEventSerializer(serializers.Serializer):
    
    title = serializers.CharField()
    date = serializers.DateField(allow_null=True, format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    time = serializers.TimeField(allow_null=True, format="%H:%M:%S", input_formats=["%H:%M:%S"])
    description = serializers.CharField()
    category = serializers.CharField()
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    
    def validate(self, attrs):

        for field in ['title', 'date', 'time', 'description', 'category']:
            if not attrs.get(field):
                raise serializers.ValidationError({"message": "All fields are required"})
            
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):   
        #seperate the image
        images_data = validated_data.pop('images')
        #create the news event object
        news_event = NewsEvent.objects.create(**validated_data)
        #create each related NewsEventImage
        for image in images_data:
            NewsEventImage.objects.create(news_event=news_event, image=image)
        
        #return the newly created news event
        return news_event

class NewsEventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsEventImage
        fields = ['image']  

class GetNewsEventSerializer(serializers.ModelSerializer):
    images = NewsEventImageSerializer(many=True)
    
    class Meta:
        model = NewsEvent
        fields = ['id', 'title', 'date', 'time', 'description', 'category', 'images']
