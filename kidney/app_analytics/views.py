from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    GetPatientAnalyticsSerializer
)
from app_authentication.models import User

class GetPatientAnalyticsView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetPatientAnalyticsSerializer
    queryset = User.objects.all()
