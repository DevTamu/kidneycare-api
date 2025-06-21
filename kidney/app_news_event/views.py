from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from kidney.utils import ResponseMessageUtils
from .serializers import (
    AddNewsEventSerializer,
    GetNewsEventSerializer,
    GetNewsEventWithIDSerializer
)
from kidney.pagination.appointment_pagination import Pagination
from .models import NewsEvent
import logging

logger = logging.getLogger(__name__)

class AddNewsEventView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddNewsEventSerializer

    def post(self, request, *args, **kwargs):

        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return ResponseMessageUtils(
                    message="Successfully Added News Event",
                    status_code=status.HTTP_201_CREATED
                )
            return ResponseMessageUtils(
                message=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
                
        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class GetNewsEventView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetNewsEventSerializer
    pagination_class = Pagination

    def get_queryset(self):
        return NewsEvent.objects.all()

    def get(self, request, *args, **kwargs):
        try:     

            queryset = self.get_queryset()

            paginator = self.pagination_class()

            paginated_data = paginator.paginate_queryset(queryset, request)

            serializer = self.get_serializer(paginated_data, many=True, context={'request': request})

            paginated_response = paginator.get_paginated_response(serializer.data)

            return ResponseMessageUtils(
                message="List of News Event Data",
                data=paginated_response.data,
                status_code=status.HTTP_200_OK
            )
        except NewsEvent.DoesNotExist:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetNewsEventWithIDView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = GetNewsEventWithIDSerializer
    lookup_field = 'pk' #capture primary key id news event

    def get_queryset(self):
        return NewsEvent.objects.filter(id=self.kwargs.get('pk')).first()

    def get(self, request, *args, **kwargs):

        try:

            news_event = self.get_queryset()

            if not news_event:
                return ResponseMessageUtils(
                    message="No news event found",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(news_event)

            return ResponseMessageUtils(
                message="News Event",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetNewsEventLimitByTwoView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GetNewsEventSerializer
    def get(self, request, *args, **kwargs):
        try:     
            #limit the display of the events
            events = NewsEvent.objects.all().order_by('created_at')[0:2]
            serializer = self.get_serializer(events, many=True, context={'request': request})
            return ResponseMessageUtils(
                message="List of News Event Data",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )
        except NewsEvent.DoesNotExist:
            return ResponseMessageUtils(
                message=f"Something went wrong while processing your request.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )