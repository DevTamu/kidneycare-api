from rest_framework import generics, status
from .serializers import (
    CreateTreatmentFormSerializer,
    GetPatientHealthMonitoringSerializer,
    GetPatientsTreatmentHistorySerializer,
    GetPatientTreatmentSerializer,
    DeletePatientsTreatmentHistorySerializer
)
from rest_framework.exceptions import ParseError
from kidney.utils import ResponseMessageUtils, extract_first_error_message, get_token_user_id
from .models import Treatment
from rest_framework.permissions import IsAuthenticated
from app_authentication.models import Caregiver
from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 10  #define how many appointments to show per page
    page_size_query_param = 'limit'  # Allow custom page size via query params
    max_page_size = 10  # Maximum allowed page size
    page_query_param = 'page'

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

class GetPatientsTreatmentHistoryView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientsTreatmentHistorySerializer
    pagination_class = Pagination
    lookup_field = 'pk'

    def get_queryset(self):
        return Treatment.objects.filter(user=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):

        try:
            treatment = self.get_queryset()
            paginator = self.pagination_class()
            paginated_data = paginator.paginate_queryset(treatment, request)
            serializer = self.get_serializer(paginated_data, many=True)
            paginated_response = paginator.get_paginated_response(serializer.data)

            return ResponseMessageUtils(
                message="List of Patient treatment history",
                data=paginated_response.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetPatientTreatmentView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientTreatmentSerializer

    def get_queryset(self):
        return Treatment.objects.filter(user=self.kwargs.get('pk'), id=self.kwargs.get('id')).first()
    

    def get(self, request, *args, **kwargs):

        try:

            treatment = self.get_queryset()

            if not treatment:
                return ResponseMessageUtils(
                    message="No treatment found",
                    data={},
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(treatment, many=False)

            return ResponseMessageUtils(
                message="Patient Hemodialysis Treatment",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeletePatientsTreatmentHistoryView(generics.DestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = DeletePatientsTreatmentHistorySerializer


    def get_queryset(self):
        pk = self.kwargs.get('pk')
        id = self.kwargs.get('id')
        return Treatment.objects.get(user=pk, id=id)
    
    def destroy(self, request, *args, **kwargs):
        
        try:
            treatment = self.get_queryset()
            treatment.delete()
            return ResponseMessageUtils(
                message="Successfully deleted the treatment history",
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

