from django.urls import path
from .views import school_list_view

urlpatterns = [
    path('', school_list_view),
]
