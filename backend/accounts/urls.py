# accounts/urls.py
from .views import generate_invite_code
from django.urls import path
from . import views
from .views import csrf_token_view
from .views import whoami_view


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),  # ← 添加这一行
    path('send_code/', views.send_verification_code, name='send_code'),
    path('generate_invite/', generate_invite_code, name='generate_invite'), 
    path('profile/', views.profile_view, name='profile'),
    path('whoami/', whoami_view, name='whoami'),
    path('csrf/', csrf_token_view, name='csrf_token')
    ]