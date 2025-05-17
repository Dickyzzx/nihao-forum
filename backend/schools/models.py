from django.db import models
from django.utils.text import slugify
from django.conf import settings

# ---------------------------
# 学校模型，每个学校对应一个板块
# ---------------------------
class School(models.Model):
    # 学校名称
    name = models.CharField(max_length=100)

    # URL 中使用的 slug，如 jhu、nyu
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        # 如果没有手动填 slug，则自动根据 name 生成 slug
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ---------------------------
# 帖子模型，每个学校可以有很多帖子
# ---------------------------
class Post(models.Model):
    # 帖子标题
    title = models.CharField(max_length=200)

    # 帖子正文内容
    content = models.TextField()

    # 所属学校（ForeignKey 外键关联 School）
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='posts')

    # 作者（关联你自定义的 CustomUser 模型）
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    # 创建时间（自动填充）
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.school.name}] {self.title}"
