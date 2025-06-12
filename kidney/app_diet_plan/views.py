from rest_framework import status, generics
from .serializers import (
    CreateDietPlanSerializer,
    GetPatientHealthStatusSerializer,
    GetPatientDietPlanLimitOneSerializer,
    GetPatientDietPlanWithIDSerializer,
    GetPatientDietPlanSerializer,
    GetDietPlanInAdminSerializer,
    GetAllDietPlansInAdminSerializer,
    GetPatientMedicationSerializer,
    GetDietPlanStatusInProviderSerializer
)
from collections import defaultdict
from rest_framework.permissions import IsAuthenticated
from .models import DietPlan, SubDietPlan
from datetime import time, datetime
from kidney.utils import get_token_user_id, ResponseMessageUtils, extract_first_error_message

class CreateDietPlanView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = CreateDietPlanSerializer
    lookup_field = 'pk'

    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data, context={'pk': kwargs.get('pk')})



            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(
                    message="Successfully Added Diet Plan",
                    status_code=status.HTTP_200_OK
                )
            print(f"WHAT WENT WRONG?: {extract_first_error_message(serializer.errors)}")
            return ResponseMessageUtils(
                message=extract_first_error_message(serializer.errors),
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request. {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetPatientHealthStatusView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientHealthStatusSerializer

    def get(self, request, *args, **kwargs):

        try:
            user_id = get_token_user_id(request)

            diet_plan = DietPlan.objects.filter(patient=user_id).first()

            if not diet_plan:
                return ResponseMessageUtils(
                    message="No diet plan found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(diet_plan)

            return ResponseMessageUtils(
                message="Patient Health Status",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetPatientDietPlanLimitOneView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientDietPlanLimitOneSerializer


    def get(self, request, *args, **kwargs):
        #define meal time ranges
        MEAL_TIME_MAPPING = {
            "Breakfast": (time(6, 0), time(11, 0)), #6:00AM - 9:00AM
            "Lunch": (time(12, 0), time(17, 0)), #12:00PM - 5:00PM
            "Dinner": (time(18, 0), time(21, 0)), #6:00PM - 9:00PM
        }
        try:
            #get the user id of the current authenticated user
            user_id = get_token_user_id(request)

            #get the first diet plans of the authenticated user
            diet_plan = DietPlan.objects.filter(patient=user_id).first()


            if not diet_plan:
                return ResponseMessageUtils(
                    message="No diet plan found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            #get the current time
            now = datetime.now().time()

            #find which meal matches the current time
            suggested_meal = None
            for meal_type, (start_time, end_time) in MEAL_TIME_MAPPING.items():
                if start_time <= now <= end_time:
                    suggested_meal = str(meal_type).lower()
                    break

            if not suggested_meal:
                return ResponseMessageUtils(message="No meal suggested at this time", status_code=status.HTTP_200_OK)

            sub_plan = SubDietPlan.objects.select_related('diet_plan').filter(
                diet_plan=diet_plan,
                meal_type=suggested_meal
            ).first()

            if not sub_plan:
                return ResponseMessageUtils(message=f"No suggested meal plan found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(sub_plan)


            return ResponseMessageUtils(
                message="Patient Suggested Meal",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        


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
                return ResponseMessageUtils(
                    message="No diet plan found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(diet_plan, many=True)

            return ResponseMessageUtils(
                message="List of Diet Plan",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetPatientDietPlanWithIDView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientDietPlanWithIDSerializer
    lookup_field = 'pk' #capture the pk in the url

    def get_queryset(self):
        return SubDietPlan.objects.filter(id=self.kwargs.get('pk'))
    
    def get(self, request, *args, **kwargs):

        try:
            diet_plan = self.get_queryset().first()

            #if no diet plan found return 404
            if not diet_plan:
                return ResponseMessageUtils(
                    message="No diet plan found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(diet_plan, many=False)

            return ResponseMessageUtils(
                message="Patient Diet Plan",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetDietPlanInAdminView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetDietPlanInAdminSerializer
    
    def get_queryset(self):


        return SubDietPlan.objects.select_related('diet_plan').filter(
            id=self.kwargs.get('sub_diet_plan_id')
        ).first()

    def get(self, request, *args, **kwargs):

        try:
            diet_plan = self.get_queryset()

            if not diet_plan:
                return ResponseMessageUtils(
                    message="No diet plan found",
                    status_code=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(diet_plan, many=False)

            return ResponseMessageUtils(
                message="Patient Diet Plan",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetAllDietPlansInAdminView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetAllDietPlansInAdminSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):

        diet_plan = DietPlan.objects.filter(patient=self.kwargs.get('pk')).first()

        return SubDietPlan.objects.filter(diet_plan=diet_plan)

    def list(self, request, *args, **kwargs):

        try:

            sub_diet_plans = self.get_queryset()

            if not sub_diet_plans:
                return ResponseMessageUtils(message="No diet plan found", status_code=status.HTTP_404_NOT_FOUND)

            
            serializer = self.get_serializer(sub_diet_plans, many=True)

            grouped_data = defaultdict(list)

            for item in serializer.data:
                meal_type = str(item['meal_type']).lower()
                grouped_data[meal_type].append(item)

            return ResponseMessageUtils(
                message="List of diet plans",
                data=grouped_data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetPatientMedicationView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientMedicationSerializer
    lookup_field = 'pk'


    def get(self, request, *args, **kwargs):

        try:
            
            user_id = get_token_user_id(request)


            if kwargs.get('pk') in (None, ""):
                diet_plan = DietPlan.objects.filter(patient=user_id)
            else:
                diet_plan = DietPlan.objects.filter(patient=user_id, id=kwargs.get('pk'))
                
            if not diet_plan:
                return ResponseMessageUtils(message="No medication found", status_code=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(diet_plan, many=True)

            return ResponseMessageUtils(
                message="List of diet plans",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class GetDietPlanStatusInProviderView(generics.RetrieveAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetDietPlanStatusInProviderSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):

        try:

            diet_plan = DietPlan.objects.filter(patient=kwargs.get('pk')).first()

            if not diet_plan:
                return ResponseMessageUtils(
                    message="No diet plan found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(diet_plan, many=False)

            return ResponseMessageUtils(
                message="Diet plan found",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )


        except Exception as e:
            return ResponseMessageUtils(
                message="Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
