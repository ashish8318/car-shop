from django.contrib.auth.models import User
from django.db import models

class TestDrive(models.Model):
    username = models.CharField(null=False, blank=False, max_length=300)
    email = models.EmailField(null=False, blank=False)

    def __str__(self) -> str:
        return f'{self.username}'
    
class UserImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(blank=True, null=True, upload_to="avatar")

    def __str__(self) -> str:
        return f'{self.avatar}'