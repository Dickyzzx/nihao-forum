import random, string, json
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.views.decorators.http import require_POST
from .models import InviteCode
from schools.models import School
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_GET
from django.core.cache import cache  # 用于临时保存验证码
from django.conf import settings

User = get_user_model()

# 临时保存验证码（建议后期改为缓存或数据库）
email_verification_codes = {}

# ------------------------
# 登录视图
# ------------------------
@csrf_protect
@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    email = data.get('email')
    password = data.get('password')

    try:
        user_obj = User.objects.get(email=email)
        username = user_obj.username
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Email not found'}, status=400)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({
            'success': True,
            'school_id': user.school.id if user.school else None,
            'school_name': user.school.name if user.school else None,
            'school_slug': user.school.slug if user.school else None  # ✅ 添加 slug
        })
    else:
        return JsonResponse({'success': False, 'message': 'Incorrect password'}, status=400)

# ------------------------
# 注册视图
# ------------------------
@csrf_protect
def register_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    username = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname')
    school_slug = data.get('school')  # ✅ 前端传 slug
    method = data.get('register_method')
    email = data.get('email')
    email_code = data.get('email_code')
    invite_code = data.get('invite_code')

    print("✅ 收到学校 slug:", school_slug)

    try:
        school = School.objects.get(slug=school_slug)
        print("✅ 数据库查到学校对象:", school)
    except School.DoesNotExist:
        print("❌ 查不到学校对象")
        school = None

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

    user = User.objects.create_user(username=username, password=password, email=email)
    user.nickname = nickname
    user.school = school
    user.save()

    if method == 'invite':
        code_obj.used = True
        code_obj.used_by = user
        code_obj.save()

    return JsonResponse({'success': True})

# ------------------------
# 发送邮箱验证码（注册用）
# ------------------------
def send_verification_code(request):
    email = request.GET.get('email')
    if not email or not email.endswith('.edu'):
        return JsonResponse({'success': False, 'message': '请输入有效的 .edu 邮箱'})
    
    #✅ 频率限制：检查 60 秒锁
    if cache.get(f'register_lock:{email}'):
        return JsonResponse({'success': False, 'message': '请勿频繁请求验证码，请稍后再试。'})

    code = str(random.randint(100000, 999999))
    email_verification_codes[email] = code

    # ✅ 设置锁定：60 秒内禁止再次请求
    cache.set(f'register_lock:{email}', True, timeout=60)

    send_mail(
        subject='nihao.com 邮箱验证码',
        message=f'您的验证码是：{code}',
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )

    return JsonResponse({'success': True, 'message': '验证码已发送，请查收邮箱'})

# ------------------------
# 邀请码生成工具函数
# ------------------------
def generate_random_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# ------------------------
# 登录用户生成邀请码
# ------------------------
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

# ------------------------
# 登录用户信息页（模板页面）
# ------------------------
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

# ------------------------
# 设置 CSRF Cookie（给前端用）
# ------------------------
@ensure_csrf_cookie
def csrf_token_view(request):
    return JsonResponse({'success': True})

# ------------------------
# 登录用户身份信息（前端调试）
# ------------------------
@login_required
def whoami_view(request):
    user = request.user
    return JsonResponse({
        "nickname": user.nickname,
        "email": user.email,
        "school": user.school.name if user.school else None,
    })

@require_GET
def send_reset_code(request):
    email = request.GET.get('email', '').strip()

    if not email.endswith('.edu'):
        return JsonResponse({'success': False, 'message': 'Only .edu emails allowed.'})

    # ✅ 防止频繁请求：60 秒内禁止重复发送
    if cache.get(f'reset_lock:{email}'):
        return JsonResponse({'success': False, 'message': '请勿频繁请求验证码，请稍后再试。'})
    
    code = ''.join(random.choices('0123456789', k=6))

    # 保存到缓存，5分钟有效
    cache.set(f'reset_code:{email}', code, timeout=300)

    # 设置请求频率锁：60 秒
    cache.set(f'reset_lock:{email}', True, timeout=60)

    try:
        send_mail(
            subject='Reset your password',
            message=f'Your password reset code is: {code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Failed to send email.'})
    

@csrf_protect
@require_POST
def reset_password_view(request):
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        code = data.get('code', '').strip()
        new_password = data.get('new_password', '').strip()

        if not email or not code or not new_password:
            return JsonResponse({'success': False, 'message': 'Missing fields.'})

        cached_code = cache.get(f'reset_code:{email}')
        if not cached_code or cached_code != code:
            return JsonResponse({'success': False, 'message': 'Invalid or expired code.'})

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)  # ✅ 正确加密密码
            user.save()
            cache.delete(f'reset_code:{email}')  # 清除验证码
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found.'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': 'Invalid request.'})