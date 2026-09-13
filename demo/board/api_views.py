from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Comment, Post
from .serializers import CommentSerializer, PostDetailSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """게시글 CRUD API.

    - list/create → /api/posts/
    - retrieve/update/partial_update/destroy → /api/posts/{pk}/
    라우팅은 Router가 자동으로 생성한다 (study7).
    """

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer  # 상세 조회에서만 댓글까지 nested로 포함
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """댓글 CRUD API. /api/comments/ 로 노출."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
