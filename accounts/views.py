import random, string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from schools.models import School
from .models import InviteCode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer

# 使用当前启用的自定义用户模型（CustomUser）
User = get_user_model()

# 临时保存验证码的字典（后续可换为缓存或数据库）
email_verification_codes = {}

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 登录成功后，跳转用户所属学校板块（若有）
            school = getattr(user, 'school', None)
            if school:
                return redirect(f'/schools/{school.slug}/')
            return redirect('/schools/')
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
        email = request.POST.get('email')
        email_code = request.POST.get('email_code')
        invite_code = request.POST.get('invite_code')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在。')
            return render(request, 'accounts/register.html', {'schools': schools})

        # 邮箱注册逻辑
        if method == 'email':
            if not email or not email.endswith('.edu'):
                messages.error(request, '必须使用 .edu 邮箱注册。')
                return render(request, 'accounts/register.html', {'schools': schools})
            stored_code = email_verification_codes.get(email)
            if not stored_code or email_code != stored_code:
                messages.error(request, '验证码错误或已过期，请重新获取。')
                return render(request, 'accounts/register.html', {'schools': schools})
            del email_verification_codes[email]

        # 邀请码注册逻辑
        elif method == 'invite':
            try:
                code_obj = InviteCode.objects.get(code=invite_code, used=False)
            except InviteCode.DoesNotExist:
                messages.error(request, '邀请码无效或已使用。')
                return render(request, 'accounts/register.html', {'schools': schools})

        # 创建新用户
        user = User.objects.create_user(username=username, password=password)
        user.first_name = display_name
        user.school = School.objects.get(slug=school_slug)
        user.save()

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
    email_verification_codes[email] = code

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
    existing = InviteCode.objects.filter(inviter=request.user, used=False).first()
    if existing:
        return JsonResponse({'code': existing.code})

    while True:
        code = generate_random_code()
        if not InviteCode.objects.filter(code=code).exists():
            break

    invite = InviteCode.objects.create(code=code, inviter=request.user)
    return JsonResponse({'code': invite.code})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')



class RegisterAPIView(APIView):
    """
    注册 API 接口视图：
    - 接收 JSON 数据
    - 使用 RegisterSerializer 验证和创建用户
    - 返回成功信息或错误详情
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': '注册成功'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
