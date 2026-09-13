# study2. 실습2 — 모델 + 마이그레이션

Notion 학습 목표 대응: **모델 + 마이그레이션**

## 1. Django 모델(ORM) 기초

Django의 모델은 Python 클래스로 DB 테이블을 정의하는 ORM(Object-Relational Mapping)입니다. SQL을 직접 쓰지 않고도 Python 코드로 테이블 생성/조회/수정/삭제가 가능합니다.

자주 쓰는 필드 타입:

| 필드 | 설명 |
|---|---|
| `CharField(max_length=N)` | 짧은 문자열 (max_length 필수) |
| `TextField()` | 긴 문자열 (글 내용 등) |
| `IntegerField()` | 정수 |
| `BooleanField()` | 참/거짓 |
| `DateTimeField(auto_now_add=True)` | 생성 시 자동으로 현재 시각 저장 |
| `DateTimeField(auto_now=True)` | 저장할 때마다 현재 시각으로 갱신 |
| `ForeignKey(Model, on_delete=...)` | 다대일(N:1) 관계 |
| `ManyToManyField(Model)` | 다대다(N:M) 관계 |

`ForeignKey`의 `on_delete` 옵션은 참조하는 대상이 삭제될 때 동작을 정의합니다. 가장 많이 쓰는 것은 `models.CASCADE`(부모가 삭제되면 자식도 함께 삭제)입니다.

## 2. 커스텀 User 모델

Django 기본 `User` 모델은 `username`, `email`, `password` 등 최소한의 필드만 가지고 있습니다. 서비스마다 닉네임, 프로필 이미지 등 추가 필드가 필요하므로, **프로젝트 시작 시점에 커스텀 User 모델을 만들어두는 것이 정석**입니다.

> ⚠️ 주의: `AUTH_USER_MODEL`은 **첫 `migrate` 실행 전**에 설정해야 합니다. 이미 기본 `auth.User`로 마이그레이션을 적용한 뒤에 바꾸면 여러 앱이 `auth.User`를 참조하고 있어 충돌이 발생합니다. (이번 실습에서도 `db.sqlite3`를 초기화하고 다시 마이그레이션했습니다.)

```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    nickname = models.CharField('닉네임', max_length=30, blank=True)
    bio = models.CharField('자기소개', max_length=150, blank=True)

    def __str__(self):
        return self.nickname or self.username
```

```python
# config/settings.py
AUTH_USER_MODEL = 'accounts.User'
```

`AbstractUser`를 상속하면 `username`, `password`, `email`, `is_staff`, `is_active` 등 기존 인증 관련 필드/메서드(비밀번호 해싱, 권한 체크 등)를 그대로 물려받으면서 필드만 추가할 수 있습니다.

## 3. 게시판 모델 설계 (Post, Comment)

```python
# board/models.py
from django.conf import settings
from django.db import models


class Post(models.Model):
    title = models.CharField('제목', max_length=100)
    content = models.TextField('내용')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='작성자',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)

    class Meta:
        ordering = ['created_at']
```

설계 포인트:

- `author`는 `settings.AUTH_USER_MODEL` 문자열로 참조합니다. `accounts.User`를 직접 import해서 쓰지 않는 이유는, 다른 앱이 User 모델을 모르더라도(또는 나중에 User 모델이 바뀌더라도) 안전하게 참조하기 위함입니다. (Django 공식 권장 방식)
- `related_name='posts'`를 지정하면 `user.posts.all()`처럼 역참조가 가능합니다. 지정하지 않으면 기본값 `post_set`이 사용됩니다.
- `Comment.post`도 `related_name='comments'`로 지정해 `post.comments.all()`로 댓글 목록을 가져올 수 있게 했습니다.
- `Meta.ordering`으로 기본 정렬(게시글은 최신순, 댓글은 오래된순)을 지정합니다.

## 4. 마이그레이션 명령어

```bash
# 1. 모델 변경사항을 감지해 마이그레이션 파일 생성
python manage.py makemigrations accounts board

# 2. 마이그레이션 파일을 실제 DB 스키마에 반영
python manage.py migrate
```

- `makemigrations`는 "무엇을 바꿀지" 파일로 기록만 합니다 (DB는 아직 안 바뀜).
- `migrate`는 그 파일을 읽어 실제 DB에 `CREATE TABLE`, `ALTER TABLE` 등을 실행합니다.
- 마이그레이션 파일(`migrations/0001_initial.py` 등)은 **Git에 커밋 대상**입니다. (팀원들이 동일한 DB 스키마 이력을 공유해야 하기 때문)

### 마이그레이션 파일 예시 구조

```python
# board/migrations/0001_initial.py (일부)
class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[...],
        ),
        ...
    ]
```

## 5. 실습2: accounts.User / board.Post / board.Comment 모델 작성

진행한 작업:

1. `accounts/models.py`에 `User(AbstractUser)` 작성 (nickname, bio 필드 추가)
2. `config/settings.py`에 `AUTH_USER_MODEL = 'accounts.User'` 추가
3. `board/models.py`에 `Post`, `Comment` 모델 작성
4. 기존 `db.sqlite3` 삭제 후 `makemigrations accounts board` → `migrate` 재실행
5. `accounts/admin.py`, `board/admin.py`에 모델을 임시로 `admin.site.register()`만 등록 (커스터마이징은 study5에서)
6. `python manage.py shell`로 모델이 정상 동작하는지 검증

### 검증 결과 (Django shell)

```python
>>> from accounts.models import User
>>> from board.models import Post, Comment
>>> u = User.objects.create_user(username='tester', password='pass12345', nickname='테스터')
>>> p = Post.objects.create(title='첫 글', content='내용입니다', author=u)
>>> c = Comment.objects.create(post=p, author=u, content='첫 댓글')
>>> p.comments.count()
1
>>> u.posts.count()
1
```

`ForeignKey`의 `related_name`을 통한 역참조(`p.comments`, `u.posts`)가 정상적으로 동작함을 확인했습니다.

> 💡 Windows 콘솔 팁: `manage.py shell`에서 한글이 포함된 객체를 `print`하면 콘솔 코드페이지(CP949) 문제로 글자가 깨져 보일 수 있습니다(데이터 자체는 정상). `set PYTHONUTF8=1` 환경변수를 설정하면 해결됩니다.

다음 문서(study3)에서는 이 모델들을 기반으로 템플릿 기반 CRUD 화면(MTV)을 만듭니다.
