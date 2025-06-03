from rest_framework.pagination import PageNumberPagination

class AppointmentPagination(PageNumberPagination):
    page_size = 20  #define how many appointments to show per page
    page_size_query_param = 'page'  # Allow custom page size via query params
    max_page_size = 25  # Maximum allowed page size