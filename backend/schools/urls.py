from django.urls import path
from .views import (
    school_list_view,
    school_board_view,
    create_post,
    post_detail_view,
    create_comment,
)

urlpatterns = [
    # 获取所有学校列表（注册下拉框）
    path('', school_list_view, name='school_list'),

    # 某个学校的帖子列表
    path('<slug:slug>/', school_board_view, name='school_board'),

    # 发帖接口
    path('<slug:slug>/post/', create_post, name='create_post'),

    # 帖子详情 + 所有评论
    path('post/<int:post_id>/', post_detail_view, name='post_detail'),

    # 发布评论
    path('post/<int:post_id>/comment/', create_comment, name='create_comment'),
]
