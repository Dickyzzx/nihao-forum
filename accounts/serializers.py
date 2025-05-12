from rest_framework import serializers
from django.contrib.auth import get_user_model
from schools.models import School

# 获取当前启用的用户模型（你定义的 CustomUser）
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器：
    - 接收用户名、密码、昵称（first_name）、所属学校
    - 创建用户并加密保存密码
    """

    # 使用学校的 slug 字段来选择学校，如 "jhu", "zju"
    school = serializers.SlugRelatedField(
        queryset=School.objects.all(),  # 限制为已存在的学校
        slug_field='slug'               # 前端提交的就是 slug 值
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'school']
        extra_kwargs = {
            'password': {'write_only': True}  # 密码不返回给前端
        }

    def create(self, validated_data):
        """
        重写 create 方法：设置密码为加密形式
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # 自动加密密码
        user.save()
        return user
