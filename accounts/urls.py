# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),  # ← 添加这一行
    path('send_code/', views.send_verification_code, name='send_code'),

]
