import datetime
from rest_framework import serializers
from .models import NewsEvent, NewsEventImage
from django.db import transaction
import os

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

class UpdateNewsEventSerializer(serializers.ModelSerializer):

    images = serializers.ListField(
        child=serializers.ImageField(), required=False
    )
    date = serializers.DateField(allow_null=True, format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    time = serializers.TimeField(allow_null=True, format="%H:%M:%S", input_formats=["%H:%M:%S"])

    class Meta:
        model = NewsEvent
        fields = ['id', 'title', 'date', 'time', 'description', 'category', 'images']


    def validate(self, attrs):

        for field in ['title', 'date', 'time', 'description', 'category']:
            if not attrs.get(field):
                raise serializers.ValidationError({"message": "All fields are required"})
        
        return attrs
    
    def update(self, instance, validated_data):

        #extract the images data
        images_data = validated_data.pop('images', None)
        print(f'qwewqeqwqe: {images_data}')
        #update instance field
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

            
        if images_data is not None:

            existing_images = list(instance.images.all())

         
            #check if the images is a list so the user can upload multiple photo
            if isinstance(images_data, list):
                for i, image in enumerate(images_data):
                    if i < len(existing_images):
                        #remove old file
                        old_image_path = existing_images[i].image.path
                        if os.path.isfile(old_image_path):
                            os.remove(old_image_path)
                        #update existing images
                        existing_images[i].image = image
                        existing_images[i].save()
                    else:
                        # Create new image if more uploaded
                        NewsEventImage.objects.create(news_event=instance, image=image)
            else:#single photo upload
                if existing_images:
                    existing_images[0].image = images_data
                    existing_images[0].save()
                else:
                    NewsEventImage.objects.create(news_event=instance, image=images_data)
        
        return instance
    

class DeleteNewsEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsEvent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DeleteNewsEventSerializer, self).__init__(args, kwargs)
        #make all the fields not required
        for field in self.fields.values():
            field.required = False
