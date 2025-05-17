from django.contrib import admin
from .models import School, Post  # ✅ 同时导入 School 和 Post 模型

# -----------------------------
# 学校模型的后台管理配置
# -----------------------------
@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    # 后台列表中显示的字段
    list_display = ['name', 'slug']

    # 当输入 name 时自动填充 slug 字段
    prepopulated_fields = {'slug': ('name',)}

# -----------------------------
# 帖子模型的后台管理配置
# -----------------------------
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 后台列表中显示的字段
    list_display = ['title', 'school', 'author', 'created_at']

    # 可搜索字段
    search_fields = ['title', 'content']

    # 可筛选字段
    list_filter = ['school', 'created_at']
