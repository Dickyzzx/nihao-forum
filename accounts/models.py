from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class InviteCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invite_codes')
    used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='used_invite_code')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} (by {self.inviter.username})"
