# study5. 실습5 — Admin 커스터마이징

Notion 학습 목표 대응: **Admin 커스터마이징**

## 1. Django Admin이란?

`django.contrib.admin`은 모델을 등록하기만 하면 CRUD가 가능한 관리자 페이지를 **자동으로 생성**해주는 Django의 대표 기능입니다. `/admin/`으로 접속하며, `createsuperuser`로 만든 관리자 계정으로 로그인합니다.

```bash
python manage.py createsuperuser
```

가장 기본적인 등록 방법 (study2에서 임시로 사용):

```python
from django.contrib import admin
from .models import Post

admin.site.register(Post)
```

이렇게만 해도 목록/추가/수정/삭제가 모두 가능한 화면이 생기지만, 실무에서는 목록에 보이는 컬럼, 검색, 필터 등을 조정해야 쓸만해집니다.

## 2. ModelAdmin 커스터마이징

`admin.ModelAdmin`을 상속한 클래스를 만들고 `@admin.register(Model)` 데코레이터로 등록하면 동작을 세밀하게 조정할 수 있습니다.

```python
# board/admin.py
from django.contrib import admin
from .models import Comment, Post


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0                                # 빈 입력 폼을 추가로 보여주지 않음
    readonly_fields = ['author', 'created_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'created_at', 'updated_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content']
```

주요 옵션 설명:

| 옵션 | 역할 |
|---|---|
| `list_display` | 목록 화면에 보여줄 컬럼 |
| `list_filter` | 목록 화면 오른쪽에 필터 사이드바 생성 |
| `search_fields` | 상단 검색창에서 검색할 필드 |
| `readonly_fields` | 상세 화면에서 수정 불가(읽기 전용)로 표시 |
| `inlines` | 연관된 다른 모델(예: 댓글)을 한 화면에서 같이 편집 |

`CommentInline`을 `PostAdmin.inlines`에 등록하면, 게시글 상세 페이지 하단에 해당 글의 댓글 목록이 표(TabularInline) 형태로 함께 나타나 **하나의 화면에서 게시글 + 댓글을 같이 관리**할 수 있습니다.

## 3. 커스텀 User 모델의 Admin

`accounts.User`는 `AbstractUser`를 상속했기 때문에, Django가 기본 제공하는 `UserAdmin`을 그대로 상속해서 확장하는 것이 안전합니다 (비밀번호 변경 폼, 권한 관리 UI 등을 그대로 재사용).

```python
# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'nickname', 'email', 'is_staff', 'date_joined']
    search_fields = ['username', 'nickname', 'email']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('nickname', 'bio')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('nickname', 'bio')}),
    )
```

- `fieldsets`: 상세(수정) 화면에서 필드를 그룹으로 묶어 보여주는 설정. 기존 `BaseUserAdmin.fieldsets`(계정 정보, 권한 등)에 "추가 정보" 그룹을 덧붙였습니다.
- `add_fieldsets`: **신규 생성** 화면 전용 필드셋. `fieldsets`와 별도로 관리됩니다 (신규 생성 시에는 비밀번호 확인 등 다른 필드 구성이 필요하기 때문).
- 커스텀 User를 그냥 `admin.site.register(User)`로 등록하면 `nickname`, `bio` 같은 추가 필드가 Admin 화면에 보이지 않으므로, 이렇게 `BaseUserAdmin`을 상속해서 필드셋을 확장해야 합니다.

## 4. 실습5: Admin 페이지 커스터마이징

진행한 작업:

1. `accounts/admin.py` — 기존 `admin.site.register(User)`를 `UserAdmin(BaseUserAdmin)` 커스텀 클래스로 교체
2. `board/admin.py` — `PostAdmin`, `CommentAdmin` 작성, `Post` 상세 화면에 `CommentInline` 추가
3. `python manage.py createsuperuser` 대신 `manage.py shell`로 관리자 계정 생성 (`admin` / 커스텀 `create_superuser` 호출)
4. `/admin/`에 로그인 후 주요 화면 동작 확인

### 확인 결과

```text
POST /admin/login/                  → 302 (로그인 성공)
GET  /admin/board/post/             → 200 (게시글 목록, list_display/list_filter/search_fields 적용됨)
GET  /admin/board/post/1/change/    → 200 (게시글 상세 + 댓글 Inline 폼 함께 표시)
GET  /admin/accounts/user/          → 200 (회원 목록, nickname 컬럼 노출)
```

이것으로 Notion 학습 목표의 "템플릿 뷰 + 회원 인증 + Admin" 축(1차 목표: 템플릿 기반 게시판+회원)을 모두 구현했습니다. 다음 문서(study6)부터는 같은 도메인(게시판+회원)을 **DRF(Django REST Framework) API**로 다시 구현하는 "고급 기술 구현" 단계로 넘어갑니다.
