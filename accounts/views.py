# accounts/views.py

import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from schools.models import School
from django.http import JsonResponse
from django.core.mail import send_mail

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
            if invite_code != 'nihao2025':  # 临时设定邀请码
                messages.error(request, '邀请码无效。')
                return render(request, 'accounts/register.html', {'schools': schools})

        # 创建用户
        user = User.objects.create_user(username=username, password=password)
        user.first_name = display_name  # 暂用 first_name 存昵称
        user.save()

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
