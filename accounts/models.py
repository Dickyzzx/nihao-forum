from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from schools.models import School


class CustomUser(AbstractUser):
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.username


class InviteCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invite_codes')
    used = models.BooleanField(default=False)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='used_invite_code')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} (by {self.inviter.username})"
