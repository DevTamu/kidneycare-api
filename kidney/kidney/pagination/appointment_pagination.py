from rest_framework.pagination import PageNumberPagination

class Pagination(PageNumberPagination):
    page_size = 10  #define how many appointments to show per page
    page_size_query_param = 'limit'  # Allow custom page size via query params
    max_page_size = 10  # Maximum allowed page size
    page_query_param = 'page'