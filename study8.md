# study8. 고급 기술 구현 3 — 퍼미션, 페이지네이션, 필터링

Notion 학습 목표 대응: **시리얼라이저, 퍼미션, 페이지네이션** 중 퍼미션 + 페이지네이션 (+ 필터링)

study7까지는 "로그인했는지"만 확인했지, "본인 글/댓글인지"는 확인하지 않았습니다. 이번 문서에서 그 문제를 해결하고, 목록 API에 페이지네이션과 검색/필터링을 추가합니다.

## 1. 커스텀 퍼미션 — IsOwnerOrReadOnly

DRF의 퍼미션 클래스는 두 단계로 검사합니다.

1. `has_permission(request, view)` : 요청 자체(뷰 단위)에 대한 허용 여부 (예: 로그인 여부)
2. `has_object_permission(request, view, obj)` : **특정 객체**에 대한 허용 여부 (예: 이 글의 작성자인가?) — `retrieve`/`update`/`destroy`처럼 객체가 정해지는 액션에서만 호출됨

study4에서 템플릿 버전에 만든 `AuthorRequiredMixin`과 동일한 역할을 DRF 퍼미션으로 구현합니다.

```python
# board/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return obj.author == request.user
```

`SAFE_METHODS`는 `('GET', 'HEAD', 'OPTIONS')`를 가리키는 상수로, "읽기 전용" 메서드를 판별할 때 관용적으로 사용합니다.

```python
# board/api_views.py
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    ...
```

퍼미션 클래스를 여러 개 나열하면 **모두 통과(AND)** 해야 허용됩니다.

- `IsAuthenticatedOrReadOnly` : 쓰기는 로그인 필요 (뷰 단위)
- `IsOwnerOrReadOnly` : 쓰기는 작성자 본인만 (객체 단위)

`CommentViewSet`에도 동일하게 적용해 "댓글도 본인 것만 수정/삭제 가능"하도록 했습니다.

## 2. 페이지네이션

게시글이 많아지면 한 번에 전체를 내려주는 것은 비효율적입니다. DRF는 전역 설정으로 페이지네이션을 켤 수 있습니다.

```python
# config/settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
    ...
}
```

`PageNumberPagination`을 켜면 목록 API 응답 형식이 배열에서 아래 구조로 바뀝니다.

```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [ ... ]
}
```

- `count` : 전체 개수, `next`/`previous` : 다음/이전 페이지 URL, `results` : 실제 데이터 배열
- `?page=2`처럼 쿼리 파라미터로 페이지를 이동합니다.
- 다른 방식으로 `LimitOffsetPagination`(`?limit=5&offset=10`)도 있으며, 무한 스크롤 UI에는 이쪽이 더 어울립니다.

## 3. 필터링 / 검색 / 정렬

`django-filter` 패키지를 설치하면 쿼리 파라미터 기반 필터링을 선언적으로 추가할 수 있습니다.

```bash
pip install django-filter
```

```python
# config/settings.py
INSTALLED_APPS = [..., 'django_filters', ...]

REST_FRAMEWORK = {
    ...
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

```python
# board/api_views.py
class PostViewSet(viewsets.ModelViewSet):
    ...
    filterset_fields = ['author']              # ?author=1  (정확히 일치하는 값으로 필터)
    search_fields = ['title', 'content']        # ?search=키워드 (여러 필드에서 부분일치 검색)
    ordering_fields = ['created_at', 'title']   # ?ordering=-created_at (정렬, -는 내림차순)
```

| 백엔드 | 쿼리 파라미터 예시 | 역할 |
|---|---|---|
| `DjangoFilterBackend` | `?author=1` | 특정 필드 값으로 정확히 필터링 |
| `SearchFilter` | `?search=Django` | 여러 필드에 걸쳐 부분 일치 검색 |
| `OrderingFilter` | `?ordering=-created_at` | 정렬 기준 지정 |

`CommentViewSet`에는 `filterset_fields = ['post']`를 추가해 `?post=1`로 특정 게시글의 댓글만 조회할 수 있게 했습니다.

## 4. 실습: 퍼미션 + 페이지네이션 + 필터링 적용

진행한 작업:

1. `board/permissions.py` — `IsOwnerOrReadOnly` 작성
2. `board/api_views.py` — `PostViewSet`/`CommentViewSet`의 `permission_classes`에 `IsOwnerOrReadOnly` 추가, `filterset_fields`/`search_fields`/`ordering_fields` 지정
3. `pip install django-filter`, `INSTALLED_APPS`에 `django_filters` 추가
4. `config/settings.py` — `REST_FRAMEWORK` 딕셔너리로 페이지네이션/필터 백엔드 전역 설정

### 검증 결과

```text
GET /api/posts/                        → {"count": 4, "next": null, "previous": null, "results": [...]}
GET /api/posts/?search=API             → 200
GET /api/posts/?ordering=title         → 200
GET /api/posts/?author=1               → 200

alice 로그인 후 bob 소유 게시글(PUT) 수정 시도  → 403 Forbidden (IsOwnerOrReadOnly가 차단)
```

이제 "로그인 사용자만 쓰기 가능(뷰 단위) + 작성자 본인만 수정/삭제(객체 단위)"가 API에서도 템플릿 버전과 동일하게 동작합니다. 다음 문서(study9)에서는 지금까지 써온 세션 인증 대신 **JWT(JSON Web Token) 인증**을 붙여봅니다.
