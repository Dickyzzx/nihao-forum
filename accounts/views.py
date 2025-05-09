# accounts/views.py

import random, string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from schools.models import School
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import InviteCode
from django.contrib.auth.decorators import login_required


# 临时保存验证码的字典（后续用缓存/数据库替换）
email_verification_codes = {}


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # 登录成功后跳转主页（暂定）
        else:
            messages.error(request, '用户名或密码错误。')
    return render(request, 'accounts/login.html')


def register_view(request):
    schools = School.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        display_name = request.POST.get('display_name')
        school_slug = request.POST.get('school')
        role = request.POST.get('role')
        year = request.POST.get('year')
        method = request.POST.get('register_method')

        # 注册方式字段
        email = request.POST.get('email')
        email_code = request.POST.get('email_code')
        invite_code = request.POST.get('invite_code')

        # 校验用户名是否重复
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在。')
            return render(request, 'accounts/register.html', {'schools': schools})

        # 注册方式校验
        if method == 'email':
            if not email or not email.endswith('.edu'):
                messages.error(request, '必须使用 .edu 邮箱注册。')
                return render(request, 'accounts/register.html', {'schools': schools})
            
            stored_code = email_verification_codes.get(email)
            if not stored_code or email_code != stored_code:
                messages.error(request, '验证码错误或已过期，请重新获取。')
                return render(request, 'accounts/register.html', {'schools': schools})
            
            # 验证成功后删除验证码
            del email_verification_codes[email]

        elif method == 'invite':
            try:
                code_obj = InviteCode.objects.get(code=invite_code, used=False)
            except InviteCode.DoesNotExist:
                messages.error(request, '邀请码无效或已使用。')
                return render(request, 'accounts/register.html', {'schools': schools})


        # 创建用户
        user = User.objects.create_user(username=username, password=password)
        user.first_name = display_name  # 暂用 first_name 存昵称
        user.save()

        # ↓ 更新邀请码状态
        if method == 'invite':
            code_obj.used = True
            code_obj.used_by = user
            code_obj.save()

        messages.success(request, '注册成功，请登录。')
        return redirect('login')

    return render(request, 'accounts/register.html', {'schools': schools})


def send_verification_code(request):
    email = request.GET.get('email')
    if not email or not email.endswith('.edu'):
        return JsonResponse({'success': False, 'message': '请输入有效的 .edu 邮箱'})

    code = str(random.randint(100000, 999999))
    email_verification_codes[email] = code  # 保存验证码（简化）

    send_mail(
        subject='nihao.com 邮箱验证码',
        message=f'您的验证码是：{code}',
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return JsonResponse({'success': True, 'message': '验证码已发送，请查收邮箱'})


def generate_random_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@login_required
def generate_invite_code(request):
    # 若已有未使用的邀请码，先返回它
    existing = InviteCode.objects.filter(inviter=request.user, used=False).first()
    if existing:
        return JsonResponse({'code': existing.code})

    # 否则生成新邀请码
    while True:
        code = generate_random_code()
        if not InviteCode.objects.filter(code=code).exists():
            break

    invite = InviteCode.objects.create(code=code, inviter=request.user)
    return JsonResponse({'code': invite.code})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')