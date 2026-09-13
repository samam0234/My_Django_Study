from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignUpForm(UserCreationForm):
    nickname = forms.CharField(label='닉네임', max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'nickname', 'password1', 'password2']
