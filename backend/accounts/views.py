import random, string, json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import InviteCode, School
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

User = get_user_model()

# 临时保存验证码的字典（后续用缓存/数据库替换）
email_verification_codes = {}

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, '用户名或密码错误。')
    return render(request, 'accounts/login.html')


@csrf_protect
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    username = data.get('email')  # 使用邮箱作为用户名
    password = data.get('password')
    nickname = data.get('nickname')
    school_name = data.get('school')
    method = data.get('register_method')
    email = data.get('email')
    email_code = data.get('email_code')
    invite_code = data.get('invite_code')

    if User.objects.filter(username=username).exists():
        return JsonResponse({'success': False, 'message': 'This email is already registered.'}, status=400)

    if method == 'email':
        if not email or not email.endswith('.edu'):
            return JsonResponse({'success': False, 'message': 'You must use a .edu email to register.'}, status=400)
        
        stored_code = email_verification_codes.get(email)
        if not stored_code or email_code != stored_code:
            return JsonResponse({'success': False, 'message': 'Invalid or expired code.'}, status=400)
        del email_verification_codes[email]

    elif method == 'invite':
        try:
            code_obj = InviteCode.objects.get(code=invite_code, used=False)
        except InviteCode.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid or used invite code.'}, status=400)

    try:
        school = School.objects.get(name=school_name)
    except School.DoesNotExist:
        school = None

    user = User.objects.create_user(username=username, password=password, email=email)
    user.nickname = nickname
    user.school = school
    user.save()

    if method == 'invite':
        code_obj.used = True
        code_obj.used_by = user
        code_obj.save()

    return JsonResponse({'success': True})


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


@ensure_csrf_cookie
def csrf_token_view(request):
    return JsonResponse({'success': True})
