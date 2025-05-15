from rest_framework import status, generics
from .serializers import (
    AddDietPlanSerializer
)
from .models import DietPlan

class AddDietPlanView(generics.CreateAPIView):

    serializer_class = AddDietPlanSerializer
    queryset = DietPlan.objects.all()