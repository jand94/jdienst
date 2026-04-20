from rest_framework.pagination import PageNumberPagination


class DefaultListPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"


class DefaultStreamPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "page_size"
