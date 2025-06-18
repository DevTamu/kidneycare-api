from django.shortcuts import render
from .serializers import (
    CreateScheduleSerializer,
    GetScheduleSerializer
)
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from .models import Schedule
from kidney.utils import ResponseMessageUtils, extract_first_error_message

class CreateScheduleView(generics.CreateAPIView):

    serializer_class = CreateScheduleSerializer
    queryset = Schedule.objects.all()

    def post(self, request, *args, **kwargs):

        try:
            
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Added Schedule Successfullly", status_code=status.HTTP_201_CREATED)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


class GetScheduleView(generics.ListAPIView):

    serializer_class = GetScheduleSerializer

    def get_queryset(self):
        return Schedule.objects.get(id=3)

    def get(self, request, *args, **kwargs):

        try:

            serializer = self.get_serializer(self.get_queryset(), many=False)

            return ResponseMessageUtils(
                message="Schedule",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        
        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )