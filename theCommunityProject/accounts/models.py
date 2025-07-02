from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    #유저 아이디
    user_id = models.CharField(max_length=12, unique=True)

    #비밀번호
    password = models.CharField(null=False, blank=False, max_length=128)

    #성별
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('N', 'None')
    ]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='N')
    
    #출생연도
    birth_year = models.PositiveIntegerField(default=2000, blank=False)
