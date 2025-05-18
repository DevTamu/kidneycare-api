from rest_framework import status, generics
from .serializers import (
    AddDietPlanSerializer,
    GetPatientDietPlanSerializer
)
from rest_framework.permissions import IsAuthenticated
from .models import DietPlan
from kidney.utils import get_token_user_id, ResponseMessageUtils

class AddDietPlanView(generics.CreateAPIView):

    serializer_class = AddDietPlanSerializer
    queryset = DietPlan.objects.all()


class GetPatientDietPlanView(generics.RetrieveAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientDietPlanSerializer

    def get(self, request, *args, **kwargs):

        try:
            user_id = get_token_user_id(request)

            diet_plan = DietPlan.objects.filter(patient=request.user)

            serializer = self.get_serializer(diet_plan, many=False)

            return ResponseMessageUtils(message="Patient Health Status", data=serializer.data, status_code=status.HTTP_200_OK)
        except Exception as e:
            print(f'qweqwewq: {e}')
            return ResponseMessageUtils(message="Something went wrong", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)