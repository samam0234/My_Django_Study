# study7. 고급 기술 구현 2 — 시리얼라이저 심화 / ViewSet / Router

Notion 학습 목표 대응: **시리얼라이저, 퍼미션, 페이지네이션** 중 시리얼라이저 심화 + ViewSet/Router

study6에서는 `APIView`로 목록/상세를 각각 직접 구현했습니다. 이번에는 같은 기능을 **ViewSet + Router**로 리팩터링해 코드량을 줄이고, `Comment`도 API로 노출합니다.

## 1. ViewSet이란?

`APIView`는 View 하나당 URL 하나가 기본이지만, REST 리소스는 보통 "목록 조회/생성"과 "단건 조회/수정/삭제"처럼 **행동 패턴이 정형화**되어 있습니다. `ViewSet`은 이 패턴을 클래스 하나로 묶고, URL 연결은 `Router`에게 위임합니다.

```python
# board/api_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Comment, Post
from .serializers import CommentSerializer, PostDetailSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer   # 상세 조회에서만 댓글 nested 포함
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

- `ModelViewSet`은 `list`, `create`, `retrieve`, `update`, `partial_update`, `destroy` 6개 액션을 모두 자동 구현합니다. (study6의 `APIView` 두 개 분량이 훨씬 짧아짐)
- `self.action`: 현재 어떤 액션이 처리 중인지(`'list'`, `'retrieve'` 등) 알려주는 속성. `get_serializer_class()`를 오버라이드해 **액션별로 다른 Serializer**를 쓸 수 있습니다.
- `perform_create()`: `serializer.save()` 직전 훅. study6에서 `APIView.post()` 안에 직접 쓰던 `serializer.save(author=request.user)` 로직을 여기로 옮겼습니다.

## 2. Router — URL 자동 생성

```python
# board/api_urls.py
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register('posts', api_views.PostViewSet, basename='api_post')
router.register('comments', api_views.CommentViewSet, basename='api_comment')

urlpatterns = router.urls
```

`router.register('posts', PostViewSet)` 한 줄이 아래 5개 URL 패턴을 자동으로 만들어줍니다.

| Method | URL | 액션 |
|---|---|---|
| GET | `/api/posts/` | list |
| POST | `/api/posts/` | create |
| GET | `/api/posts/{pk}/` | retrieve |
| PUT/PATCH | `/api/posts/{pk}/` | update/partial_update |
| DELETE | `/api/posts/{pk}/` | destroy |

`DefaultRouter`는 추가로 API 루트(`/api/`)에서 등록된 리소스 목록을 보여주는 탐색용 화면도 만들어줍니다.

## 3. 시리얼라이저 심화 — Nested Serializer, SerializerMethodField

```python
# board/serializers.py
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']  # post는 쓰기 허용(어느 글인지 지정 필요)


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'comment_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.count()


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)  # nested serializer

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
```

- **SerializerMethodField**: 모델 필드에 없는 값을 계산해서 넣고 싶을 때 사용. `get_<필드명>(self, obj)` 메서드의 반환값이 그대로 필드 값이 됩니다. 여기서는 댓글 개수(`comment_count`)를 계산합니다.
- **Nested Serializer**: `comments = CommentSerializer(many=True, read_only=True)`처럼 다른 Serializer를 필드로 중첩하면, 연관된 객체들을 통째로 JSON에 포함시킬 수 있습니다.
- **목록/상세에서 다른 응답 크기**: 목록(`PostSerializer`)은 댓글 개수만, 상세(`PostDetailSerializer`)는 댓글 전체 내용까지 포함하도록 나눴습니다. 목록 API에서 모든 게시글의 댓글까지 매번 전부 내려주면 응답이 불필요하게 무거워지기 때문입니다.

## 4. 실습: ViewSet/Router 전환 + Comment API 추가

진행한 작업:

1. `board/serializers.py` — `CommentSerializer`, `comment_count`를 가진 `PostSerializer`, 댓글을 nested로 포함하는 `PostDetailSerializer` 작성
2. `board/api_views.py` — study6의 `APIView` 2개를 `PostViewSet`, `CommentViewSet`(둘 다 `ModelViewSet`)으로 교체
3. `board/api_urls.py` — `DefaultRouter`로 URL 자동 생성 (수동 `path()` 나열 제거)

### 검증 결과

```text
GET /api/posts/1/  → 200
{
  "id": 1, "title": "첫 글", "author": "tester", "comment_count": 2,
  "comments": [
    {"id": 1, "post": 1, "author": "tester", "content": "첫 댓글", ...},
    {"id": 2, "post": 1, "author": "bob", "content": "Bob의 댓글", ...}
  ]
}

POST /api/comments/  (로그인, {"post": 1, "content": "viewset comment test"})
→ 201 {"id": 3, "post": 1, "author": "bob", "content": "viewset comment test", ...}
```

상세 조회에서는 댓글이 nested로 함께 오고, `/api/comments/`로 별도 댓글 생성도 가능함을 확인했습니다.

> ⚠️ 여전히 남은 문제: `CommentViewSet`도 `IsAuthenticatedOrReadOnly`만 걸려있어 **로그인한 사용자면 누구나 다른 사람 댓글을 수정/삭제**할 수 있습니다. 다음 문서(study8)에서 커스텀 퍼미션(`IsOwnerOrReadOnly`)으로 이 문제를 해결하고, 페이지네이션/필터링도 추가합니다.
