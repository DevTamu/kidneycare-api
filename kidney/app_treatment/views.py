from django.shortcuts import render
from rest_framework import generics, status
from .serializers import (
    CreateTreatmentFormSerializer
)
from .models import Treatment
from kidney.utils import ResponseMessageUtils, extract_first_error_message

from rest_framework.permissions import IsAuthenticated

class CreateTreatmentFormView(generics.CreateAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = CreateTreatmentFormSerializer
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data, context={'pk': self.kwargs.get('pk')})

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Created Treatment Form Successfully", status_code=status.HTTP_201_CREATED)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
