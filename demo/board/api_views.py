from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Comment, Post
from .permissions import IsOwnerOrReadOnly
from .serializers import CommentSerializer, PostDetailSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """게시글 CRUD API. 라우팅은 Router가 자동 생성 (study7)."""

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    filterset_fields = ['author']          # ?author=1
    search_fields = ['title', 'content']   # ?search=키워드
    ordering_fields = ['created_at', 'title']  # ?ordering=-created_at

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """댓글 CRUD API. /api/comments/ 로 노출."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filterset_fields = ['post']            # ?post=1 로 특정 글의 댓글만 조회

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
