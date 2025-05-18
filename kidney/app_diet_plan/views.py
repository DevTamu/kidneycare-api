from rest_framework import status, generics
from .serializers import (
    AddDietPlanSerializer,
    GetPatientHealthStatusSerializer,
    GetPatientDietPlanSerializer
)
from rest_framework.permissions import IsAuthenticated
from .models import DietPlan
from kidney.utils import get_token_user_id, ResponseMessageUtils

class AddDietPlanView(generics.CreateAPIView):

    serializer_class = AddDietPlanSerializer
    queryset = DietPlan.objects.all()


class GetPatientHealthStatusView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientHealthStatusSerializer

    def get(self, request, *args, **kwargs):

        try:
            user_id = get_token_user_id(request)

            diet_plan = DietPlan.objects.filter(patient=user_id).order_by('created_at').first()

            serializer = self.get_serializer(diet_plan)

            return ResponseMessageUtils(message="Patient Health Status", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetPatientDietPlanView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientDietPlanSerializer


    def get(self, request, *args, **kwargs):

        try:
            #get the user id of the current authenticated user
            user_id = get_token_user_id(request)

            #get the first diet plans of the authenticated user
            diet_plan = DietPlan.objects.filter(patient=user_id).order_by('created_at').first()

            serializer = self.get_serializer(diet_plan)

            return ResponseMessageUtils(message="Patient Diet Plan", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class GetPatientAllDietPlanView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientDietPlanSerializer


    def get(self, request, *args, **kwargs):

        try:
            #get the user id of the current authenticated user
            user_id = get_token_user_id(request)

            #get the diet plans of the authenticated user
            diet_plan = DietPlan.objects.filter(patient=user_id)

            serializer = self.get_serializer(diet_plan, many=True)

            return ResponseMessageUtils(message="List of Diet Plan", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)