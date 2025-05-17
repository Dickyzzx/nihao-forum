from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

from .models import School, Post, Comment

# -------------------------------
# 获取所有学校信息（用于注册下拉框）
# 返回 [{"name": ..., "slug": ...}, ...]
# -------------------------------
def school_list_view(request):
    schools = School.objects.all()  # 获取所有学校对象
    data = [{"name": s.name, "slug": s.slug} for s in schools]  # 提取字段构建 JSON 列表
    return JsonResponse(data, safe=False)  # 返回 JSON 列表


# -------------------------------
# 获取某学校的所有帖子（用于学校板块页）
# URL: /school/<slug:slug>/
# 返回 { school: ..., posts: [...] }
# -------------------------------
def school_board_view(request, slug):
    try:
        school = School.objects.get(slug=slug)  # 根据 slug 查找学校
    except School.DoesNotExist:
        return JsonResponse({'error': 'School not found'}, status=404)

    posts = Post.objects.filter(school=school).order_by('-created_at')  # 获取学校的所有帖子

    post_list = [  # 转换为 JSON 结构
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author": post.author.nickname if post.author else "Anonymous",
            "created_at": post.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for post in posts
    ]

    return JsonResponse({
        "school": school.name,
        "posts": post_list
    })


# -------------------------------
# 发帖接口（仅登录用户）
# URL: /school/<slug:slug>/post/
# 接收 JSON {"title": ..., "content": ...}
# 返回 {"success": true, post: {...}} 或错误信息
# -------------------------------
@csrf_exempt
@require_POST
@login_required
def create_post(request, slug):
    try:
        school = School.objects.get(slug=slug)  # 查找学校
    except School.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'School not found'}, status=404)

    try:
        data = json.loads(request.body)  # 解析请求体
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()

        if not title or not content:
            return JsonResponse({'success': False, 'message': 'Title and content required'}, status=400)

        post = Post.objects.create(  # 创建帖子
            title=title,
            content=content,
            school=school,
            author=request.user
        )

        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'title': post.title,
                'content': post.content,
                'created_at': post.created_at.isoformat()
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)


# -------------------------------
# 获取某帖详情及其评论（含嵌套回复）
# URL: /school/post/<int:post_id>/
# 返回帖内容 + 一级评论 + 每条评论的 replies 列表
# -------------------------------
def post_detail_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)  # 获取帖子对象
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post not found'}, status=404)

    # 获取所有一级评论（没有 parent 的）
    root_comments = Comment.objects.filter(post=post, parent__isnull=True).order_by('created_at')

    # 将评论与其回复转换成 JSON
    def serialize_comment(comment):
        return {
            'id': comment.id,
            'author': comment.author.nickname if comment.author else 'Anonymous',
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
            'replies': [  # 嵌套显示所有该评论的回复
                {
                    'id': r.id,
                    'author': r.author.nickname if r.author else 'Anonymous',
                    'content': r.content,
                    'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
                }
                for r in comment.replies.all().order_by('created_at')
            ]
        }

    comment_list = [serialize_comment(c) for c in root_comments]  # 构造最终评论列表

    return JsonResponse({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': post.author.nickname if post.author else 'Anonymous',
        'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
        'comments': comment_list
    })


# -------------------------------
# 发表评论（仅登录用户）
# URL: /school/post/<int:post_id>/comment/
# 接收 JSON {"content": "...", "parent_id": 可选}
# 返回成功的评论 JSON
# -------------------------------
@csrf_exempt
@require_POST
@login_required
def create_comment(request, post_id):
    try:
        post = Post.objects.get(id=post_id)  # 找到所属的帖子
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post not found'}, status=404)

    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')  # ✅ 可选：指定回复哪条评论

        if not content:
            return JsonResponse({'success': False, 'message': 'Content required'}, status=400)

        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
            except Comment.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Parent comment not found'}, status=400)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent=parent  # ✅ 指定父评论
        )

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'author': comment.author.nickname if comment.author else 'Anonymous',
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)
