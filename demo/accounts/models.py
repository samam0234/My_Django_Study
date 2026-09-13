from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """기본 User에 자기소개/닉네임을 추가한 커스텀 회원 모델.

    프로젝트 시작 시점에 AUTH_USER_MODEL로 지정해두면,
    이후 회원 관련 필드를 자유롭게 확장할 수 있다.
    """

    nickname = models.CharField('닉네임', max_length=30, blank=True)
    bio = models.CharField('자기소개', max_length=150, blank=True)

    def __str__(self):
        return self.nickname or self.username
