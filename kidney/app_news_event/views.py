from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from kidney.utils import ResponseMessageUtils
from .serializers import (
    AddNewsEventSerializer,
    GetNewsEventSerializer
)
from .models import NewsEvent
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
    serializer_class = GetNewsEventSerializer
    
    def get(self, request, *args, **kwargs):
        try:     
            events = NewsEvent.objects.all()       
            serializer = self.get_serializer(events, many=True, context={'request': request})
            return ResponseMessageUtils(message="List of News Event Data",data=serializer.data, status_code=status.HTTP_200_OK)
        except NewsEvent.DoesNotExist:
            return ResponseMessageUtils(message="Event not found", status_code=status.HTTP_404_NOT_FOUND)    


class GetNewsEventLimitByTwoView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetNewsEventSerializer
    def get(self, request, *args, **kwargs):
        try:     
            #limit the display of the events
            events = NewsEvent.objects.all().order_by('created_at')[0:2]
            serializer = self.get_serializer(events, many=True, context={'request': request})
            return ResponseMessageUtils(message="List of News Event Data",data=serializer.data, status_code=status.HTTP_200_OK)
        except NewsEvent.DoesNotExist:
            return ResponseMessageUtils(message="Event not found", status_code=status.HTTP_404_NOT_FOUND)  