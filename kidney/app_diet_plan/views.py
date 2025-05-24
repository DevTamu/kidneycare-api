from rest_framework import status, generics
from .serializers import (
    AddDietPlanSerializer,
    GetPatientHealthStatusSerializer,
    GetPatientDietPlanSerializer,
    GetPatientDietPlanWithIDSerializer
)
from rest_framework.permissions import IsAuthenticated
from .models import DietPlan
from kidney.utils import get_token_user_id, ResponseMessageUtils, extract_first_error_message

class AddDietPlanView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = AddDietPlanSerializer

    def post(self, request, *args, **kwargs):

        try:
            
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(message="Successfully Added Diet Plan", status_code=status.HTTP_200_OK)
            return ResponseMessageUtils(message=extract_first_error_message(serializer.errors), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f'WHAT WENT WRONG?: {e}')
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPatientHealthStatusView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientHealthStatusSerializer

    def get(self, request, *args, **kwargs):

        try:
            user_id = get_token_user_id(request)

            diet_plan = DietPlan.objects.filter(patient=user_id).order_by('created_at').first()

            if not diet_plan:
                return ResponseMessageUtils(message="No diet plan found", status_code=status.HTTP_404_NOT_FOUND)

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

            print(f'qwewqe: {diet_plan}')

            if not diet_plan:
                return ResponseMessageUtils(message="No diet plan found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(diet_plan, many=False)

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

            if not diet_plan:
                return ResponseMessageUtils(message="No diet plan found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(diet_plan, many=True)

            return ResponseMessageUtils(message="List of Diet Plan", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetPatientDietPlanWithIDView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientDietPlanWithIDSerializer
    lookup_field = 'pk' #capture the pk in the url

    def get_queryset(self):
        return DietPlan.objects.filter(id=self.kwargs.get('pk'))

    def get(self, request, *args, **kwargs):

        try:
            diet_plan = self.get_queryset().first()

            #if no diet plan found return 404
            if not diet_plan:
                return ResponseMessageUtils(message="No diet plan found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(diet_plan, many=False)

            return ResponseMessageUtils(message="Patient Diet Plan", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)