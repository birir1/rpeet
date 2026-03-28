"""
Custom pagination for KCK API.
"""
from rest_framework.pagination import PageNumberPagination


class KCKPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100
