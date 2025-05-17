from django.urls import path
from .views import school_list_view, school_board_view

urlpatterns = [
    path('', school_list_view),
    path('<int:school_id>/', school_board_view, name='school_board'),  # ✅ 新增

]
