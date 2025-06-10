from rest_framework import generics, status
from .serializers import (
    CreateTreatmentFormSerializer,
    GetPatientHealthMonitoringSerializer
)
from rest_framework.exceptions import ParseError
from kidney.utils import ResponseMessageUtils, extract_first_error_message, get_token_user_id
from .models import Treatment
from rest_framework.permissions import IsAuthenticated
from app_authentication.models import Caregiver

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
        except ParseError as e:
            return ResponseMessageUtils(
                message=f"Invalid JSON: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GetPatientHealthMonitoringView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientHealthMonitoringSerializer

    def get_queryset(self):
        user_id = get_token_user_id(self.request)
        return Treatment.objects.filter(user=user_id)

    def list(self, request, *args, **kwargs):

        try:

            user_id = get_token_user_id(self.request)

            queryset = self.get_queryset()

            if not queryset.exists():
                return ResponseMessageUtils(
                    message="No patient monitoring found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(queryset, context={'user_id': user_id})

            return ResponseMessageUtils(
                message="Patient health monitoring",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetAssignedPatientHealthMonitoringView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientHealthMonitoringSerializer

    def get_queryset(self):
        user_id = get_token_user_id(self.request)
        return Caregiver.objects.filter(user=user_id).first()

    def get(self, request, *args, **kwargs):

        try:

            treatment = None

            queryset = self.get_queryset()

            if not queryset:
                return ResponseMessageUtils(
                    message="No caregiver found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            treatment = Treatment.objects.filter(user=queryset.added_by).first()

            if not treatment:
                return ResponseMessageUtils(
                    message="No treatment found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(treatment, many=False, context={'user_id': queryset.added_by})

            return ResponseMessageUtils(
                message="Patient health monitoring",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


