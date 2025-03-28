# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from schools.models import School


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # 登录成功后跳转主页（暂定）
        else:
            messages.error(request, 'Invalid username or password.')
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

        # 注册方式校验（简化逻辑，后续细化）
        if method == 'email':
            if not email.endswith('.edu'):
                messages.error(request, '必须使用 .edu 邮箱注册。')
                return render(request, 'accounts/register.html', {'schools': schools})
            if email_code != '123456':  # 临时假设验证码是 123456
                messages.error(request, '验证码错误。')
                return render(request, 'accounts/register.html', {'schools': schools})
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
