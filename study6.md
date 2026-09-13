# study6. 고급 기술 구현 1 — DRF 시작

Notion 학습 목표 대응: **Django REST Framework로 API**

지금까지(study1~study5)는 Django 템플릿(MTV)으로 게시판을 만들었습니다. 이제부터는 같은 `board` 도메인을 **JSON API**로 다시 노출합니다. 프론트엔드(React/Vue 등)나 모바일 앱이 붙을 수 있도록 하는 것이 목적입니다.

## 1. DRF란?

DRF(Django REST Framework)는 Django 위에서 REST API를 쉽게 만들 수 있게 해주는 서드파티 라이브러리입니다. Django의 Model/ORM은 그대로 재사용하고, "화면(Template) 대신 JSON을 반환"하는 계층만 추가하는 구조입니다.

```bash
pip install djangorestframework
```

```python
# config/settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',   # 반드시 등록
    'accounts',
    'board',
]
```

## 2. Serializer — Model ↔ JSON 변환기

템플릿 방식의 `ModelForm`이 "Model ↔ HTML 폼"을 변환했다면, DRF의 `Serializer`는 "Model ↔ JSON"을 변환합니다.

```python
# board/serializers.py
from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
```

- `ModelSerializer`는 `ModelForm`처럼 모델 필드를 보고 자동으로 직렬화 필드를 생성합니다.
- `author = serializers.ReadOnlyField(source='author.username')` : 응답 JSON에는 `author` 필드에 User의 PK(정수)가 아니라 `username` 문자열이 나오도록 지정. `source`는 어떤 속성에서 값을 가져올지를 가리킵니다.
- `read_only_fields`: 클라이언트가 요청 본문(payload)으로 보내더라도 무시되는(서버가 채우는) 필드.

## 3. APIView — DRF의 기본 View

DRF의 `APIView`는 Django의 View와 비슷하지만, HTTP 메서드별로 메서드를 구현하고 `Request`/`Response` 객체(자동 JSON 파싱/렌더링)를 사용합니다.

```python
# board/api_views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post
from .serializers import PostSerializer


class PostListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        serializer = PostSerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

`many=True`는 리스트(QuerySet)를 직렬화할 때 필요합니다. 단일 객체는 `many` 없이 바로 넘깁니다.

`serializer.is_valid(raise_exception=True)`: 검증 실패 시 자동으로 400 응답을 던져줍니다(직접 `if not serializer.is_valid(): return Response(...)`를 쓸 필요가 없어짐).

## 4. IsAuthenticatedOrReadOnly

`permission_classes = [IsAuthenticatedOrReadOnly]` : DRF가 기본 제공하는 권한 클래스로, **읽기(GET/HEAD/OPTIONS)는 누구나 허용, 쓰기(POST/PUT/DELETE 등)는 로그인한 사용자만 허용**합니다.

> ⚠️ 지금 구현은 "로그인만 하면" 아무 글이나 수정/삭제할 수 있는 상태입니다 (작성자 본인 확인 로직이 없음). study4의 `AuthorRequiredMixin`에 해당하는 것을 DRF에도 적용해야 하는데, 이는 study8("퍼미션")에서 `IsOwnerOrReadOnly` 커스텀 퍼미션으로 해결합니다.

## 5. API용 URL 라우팅

```python
# board/api_urls.py
from django.urls import path
from . import api_views

urlpatterns = [
    path('posts/', api_views.PostListAPIView.as_view(), name='api_post_list'),
    path('posts/<int:pk>/', api_views.PostDetailAPIView.as_view(), name='api_post_detail'),
]
```

```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('board/', include('board.urls')),      # 템플릿 버전 (study1~study5)
    path('api/', include('board.api_urls')),    # API 버전 (study6~)
]
```

템플릿 라우트(`/board/`)와 API 라우트(`/api/`)를 **같은 프로젝트, 같은 모델**로 공존시킨 것이 이번 실습의 핵심입니다. 같은 `Post` 모델을 화면으로도, JSON으로도 서비스할 수 있습니다.

## 6. 실습: DRF 시작 + Post 목록/상세 API 구현

진행한 작업:

1. `pip install djangorestframework`, `INSTALLED_APPS`에 등록
2. `board/serializers.py` — `PostSerializer` 작성
3. `board/api_views.py` — `PostListAPIView`(목록/생성), `PostDetailAPIView`(조회/수정/삭제) 작성
4. `board/api_urls.py` 작성, `config/urls.py`에 `/api/` prefix로 연결

### 검증 결과 (curl)

```text
GET  /api/posts/                        → 200, JSON 배열 반환
POST /api/posts/  (비로그인)             → 403 (IsAuthenticatedOrReadOnly)
POST /api/posts/  (로그인, 세션 인증)     → 201, author가 request.user로 자동 지정됨
GET  /api/posts/5/                       → 200
PUT  /api/posts/5/  (작성자 본인)         → 200
DELETE /api/posts/5/ (작성자 본인)        → 204
```

세션 기반 인증(`SessionAuthentication`, DRF 기본 포함)을 사용했기 때문에, 브라우저/curl에서 쓰기 요청을 보낼 때는 템플릿 폼과 마찬가지로 `X-CSRFToken` 헤더가 필요했습니다.

다음 문서(study7)에서는 이 두 개의 View(List/Detail)를 `ViewSet` + `Router`로 리팩터링하고, `Comment`도 함께 API로 노출합니다.
