from django.shortcuts import render
from django.http import JsonResponse
from .models import School, Post  # ✅ 同时导入 School 和 Post 模型

# -------------------------------
# 获取所有学校信息（用于注册下拉选择）
# 返回 [{"name": ..., "slug": ...}, ...]
# -------------------------------
def school_list_view(request):
    schools = School.objects.all()
    data = [{"name": s.name, "slug": s.slug} for s in schools]
    return JsonResponse(data, safe=False)

# -------------------------------
# 获取某学校的所有帖子（前端登录后跳转此页）
# URL: /school/<school_id>/
# 返回 { school: ..., posts: [...] }
# -------------------------------
def school_board_view(request, school_id):
    try:
        # 查找该学校对象
        school = School.objects.get(id=school_id)
    except School.DoesNotExist:
        return JsonResponse({'error': 'School not found'}, status=404)

    # 从数据库中获取该学校下的帖子，按发布时间倒序排列
    posts = Post.objects.filter(school=school).order_by('-created_at')

    # 构造 JSON 可序列化的帖子列表（只包含前端需要的字段）
    post_list = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author": post.author.nickname if post.author else "Anonymous",
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for post in posts
    ]

    # 返回学校名称和对应的帖子列表
    return JsonResponse({
        "school": school.name,
        "posts": post_list
    })
