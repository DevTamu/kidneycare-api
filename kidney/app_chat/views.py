from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework import status
from kidney.utils import ResponseMessageUtils
from django.db.models import Q
import logging
logger = logging.getLogger(__name__)
from .serializers import (
    GetUsersMessageSerializer
)
from django.shortcuts import get_object_or_404
from .models import Message

class GetUsersMessageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetUsersMessageSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Message.objects.all()
    
    def get_object(self):
        
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        #get the current user
        user = self.request.user

        #filter the queryset to include only messages between the logged-in user and the user with the given ID
        queryset = self.filter_queryset(self.get_queryset().filter(
            Q(sender=user, receiver__id=id) |
            Q(sender__id=id, receiver=user)
        ))

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        obj = get_object_or_404(queryset, **filter_kwargs)

        #may raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj



       
        

