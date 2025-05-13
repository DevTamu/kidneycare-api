from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from kidney.utils import ResponseMessageUtils
from .serializers import (
    AddNewsEventSerializer,
    GetNewsEventSerializer,
    UpdateNewsEventSerializer,
    DeleteNewsEventSerializer
)
from .models import NewsEvent, NewsEventImage
import logging

logger = logging.getLogger(__name__)

class AddNewsEventView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddNewsEventSerializer

    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Successfully Added News Event", status_code=status.HTTP_201_CREATED)
            logger.error(f"Logger Error: {str(serializer.errors)}")
            logger.debug(f"Logger Debug: {str(serializer.errors)}")
            
            return ResponseMessageUtils(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return ResponseMessageUtils(message=f"Error occured during creation: {e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class GetNewsEventView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request, *args, **kwargs):
        try:     
            events = NewsEvent.objects.all()       
            serializer = GetNewsEventSerializer(events, many=True, context={'request': request})
            return ResponseMessageUtils(message="List of News Event Data",data=serializer.data, status_code=status.HTTP_200_OK)
        except NewsEvent.DoesNotExist:
            return ResponseMessageUtils(message="Event not found", status_code=status.HTTP_404_NOT_FOUND)    


class UpdateNewsEventView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UpdateNewsEventSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return NewsEvent.objects.get(id=self.kwargs.get('pk'))
    
    def patch(self, request, *args, **kwargs):
           
        try:        
            serializer = self.get_serializer(instance=self.get_queryset(), data=request.data, context={'request': request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Updated Successfully", status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)    

class DeleteNewsEventView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = DeleteNewsEventSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return NewsEvent.objects.get(id=self.kwargs.get('pk'))

    def delete(self, request, *args, **kwargs):
        
        try:
            instance = self.get_queryset()
            instance.delete()
            return ResponseMessageUtils(message="Successfully Deleted", status_code=status.HTTP_200_OK)
        except NewsEvent.DoesNotExist:
            return ResponseMessageUtils(message="News event not found", status_code=status.HTTP_400_BAD_REQUEST)    
        except Exception as e:
            print(f'qwewqeqwe: {str(e)}')
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)    