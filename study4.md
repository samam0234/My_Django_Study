# study4. 실습4 — 세션 로그인 (회원 인증)

Notion 학습 목표 대응: **세션 로그인 vs JWT** 중 세션 로그인 부분 (JWT는 study9)

## 1. Django 인증 시스템 개요

`django.contrib.auth`는 Django에 기본 내장된 인증 앱입니다. 회원가입/로그인/로그아웃, 비밀번호 해싱, 권한(permission) 체크까지 기본 기능으로 제공합니다.

- **세션 기반 인증**: 로그인에 성공하면 서버가 세션을 생성하고, 세션 ID를 쿠키로 브라우저에 저장합니다. 이후 요청마다 쿠키의 세션 ID로 사용자를 식별합니다. (`django.contrib.sessions` 미들웨어가 처리)
- `request.user` : 현재 요청을 보낸 사용자 객체. 로그인 안 했으면 `AnonymousUser` 인스턴스.
- `request.user.is_authenticated` : 로그인 여부를 판별하는 속성 (Boolean).

## 2. 회원가입 (SignUpForm)

Django는 `UserCreationForm`을 기본 제공하지만, `username`/`password1`/`password2`만 다룹니다. 우리는 `nickname` 필드를 추가로 받아야 하므로 상속해서 확장합니다.

```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    nickname = forms.CharField(label='닉네임', max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'nickname', 'password1', 'password2']
```

`UserCreationForm`은 비밀번호를 그대로 저장하지 않고 Django의 비밀번호 해셔(`PBKDF2` 등)로 해싱해서 저장합니다. 이 과정을 직접 구현할 필요가 없습니다.

```python
# accounts/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
```

## 3. 로그인 / 로그아웃 (내장 View 재사용)

Django는 로그인/로그아웃 View를 이미 제공합니다. `django.contrib.auth.views`의 `LoginView`, `LogoutView`를 그대로 가져다 쓰면 됩니다.

```python
# accounts/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
```

- `LoginView`는 `AuthenticationForm`으로 아이디/비밀번호를 검증하고, 성공 시 세션을 만든 뒤 `LOGIN_REDIRECT_URL`로 리다이렉트합니다.
- `LogoutView`는 세션을 파기(로그아웃)합니다. **Django 4.1+부터 보안상 GET 요청으로는 로그아웃할 수 없고 POST만 허용**되므로, 템플릿에서도 `<a href>`가 아니라 `<form method="post">` + `{% csrf_token %}`으로 구현해야 합니다.

```python
# config/settings.py
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'board:post_list'
LOGOUT_REDIRECT_URL = 'board:post_list'
```

## 4. 로그인 필요 뷰 보호: LoginRequiredMixin

CBV에 `LoginRequiredMixin`을 섞으면(mixin), 로그인하지 않은 사용자가 접근할 때 자동으로 `LOGIN_URL`로 리다이렉트됩니다.

```python
# board/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']  # author는 폼에서 제거!

    def form_valid(self, form):
        form.instance.author = self.request.user  # 로그인 사용자로 자동 지정
        return super().form_valid(form)
```

study3에서는 `author`를 폼에서 직접 선택하게 했지만, 이제 로그인 사용자가 있으므로 `fields`에서 `author`를 빼고 `form_valid()`에서 `self.request.user`로 자동 채웁니다. Mixin은 **왼쪽에서부터 순서대로 적용**되므로, `LoginRequiredMixin`을 항상 Generic View보다 왼쪽(먼저)에 둡니다.

## 5. 작성자 본인만 수정/삭제: 커스텀 권한 Mixin

`UserPassesTestMixin`을 사용하면 `test_func()`이 `True`를 반환할 때만 접근을 허용합니다. `False`면 기본적으로 **403 Forbidden**을 반환합니다.

```python
class AuthorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content']


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('board:post_list')
```

`LoginRequiredMixin`을 먼저 두는 이유: 비로그인 사용자는 "로그인 페이지로 리다이렉트"되는 게 자연스럽고, 로그인은 했지만 작성자가 아닌 사용자만 403을 받는 것이 사용자 경험상 맞습니다.

## 6. 댓글 작성 기능 추가 (로그인 사용자 전용)

study3에서 읽기 전용이었던 댓글에 작성 기능을 추가했습니다.

```python
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ['content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('board:post_detail', kwargs={'pk': self.kwargs['pk']})
```

상세 페이지(`post_detail.html`)에서는 로그인 여부에 따라 댓글 입력창 또는 로그인 유도 문구를 분기 처리합니다.

```html
{% if user.is_authenticated %}
<form method="post" action="{% url 'board:comment_create' post.pk %}">
    {% csrf_token %}
    <textarea name="content" rows="2" required></textarea>
    <button type="submit">댓글 등록</button>
</form>
{% else %}
<p><a href="{% url 'accounts:login' %}">로그인</a> 후 댓글을 작성할 수 있습니다.</p>
{% endif %}
```

## 7. get_absolute_url — 모델에 기본 이동 경로 지정

`CreateView`/`UpdateView`는 `success_url`을 지정하지 않으면 모델의 `get_absolute_url()`을 호출해 이동 경로를 결정합니다. 처음엔 이 메서드가 없어서 글 작성 직후 `ImproperlyConfigured` 오류가 발생했습니다.

```python
# board/models.py
from django.urls import reverse

class Post(models.Model):
    ...
    def get_absolute_url(self):
        return reverse('board:post_detail', kwargs={'pk': self.pk})
```

이 메서드를 추가하면 `PostCreateView`, `PostUpdateView` 모두 별도 `success_url` 지정 없이 자동으로 "작성/수정한 글의 상세 페이지"로 이동합니다.

## 8. 실습4: 회원가입/로그인/로그아웃 + 권한 적용

진행한 작업:

1. `accounts/forms.py` — `SignUpForm(UserCreationForm)` 작성
2. `accounts/views.py` — `SignUpView(CreateView)` 작성
3. `accounts/urls.py` — signup/login/logout 라우팅 (로그인/로그아웃은 Django 내장 View 재사용)
4. `accounts/templates/accounts/signup.html`, `login.html` 작성
5. `config/settings.py`에 `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL` 추가
6. `templates/base.html` 네비게이션에 로그인 상태별 로그인/회원가입/로그아웃 UI 추가
7. `board/views.py` — `PostCreateView`에 `LoginRequiredMixin` 적용, `author`를 `request.user`로 자동 지정
8. `board/views.py` — `AuthorRequiredMixin` 작성, `PostUpdateView`/`PostDeleteView`에 적용(본인 글만 수정/삭제)
9. `board/views.py` — `CommentCreateView` 추가 (로그인 사용자만 댓글 작성 가능)
10. `board/models.py` — `Post.get_absolute_url()` 추가

### 검증 결과

```text
비로그인 상태로 글쓰기 시도      → 302 (로그인 페이지로 리다이렉트)
회원가입(alice) → 302
로그인(alice) → 302
로그인 상태로 글 작성           → 302 (상세 페이지로 이동, author=alice로 자동 저장됨)
회원가입/로그인(bob)
bob이 alice 글 수정 시도        → 403 Forbidden (AuthorRequiredMixin)
bob이 alice 글에 댓글 작성      → 302 (성공, 댓글은 작성자 제한 없음)
```

의도한 대로 "로그인해야 글쓰기/댓글쓰기 가능", "본인 글만 수정/삭제 가능"이 모두 동작함을 확인했습니다. 다음 문서(study5)에서는 Django 기본 제공 Admin 페이지를 커스터마이징합니다.
