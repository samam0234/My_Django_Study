from rest_framework import serializers

from .models import Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        # post: 어느 게시글에 달리는 댓글인지 클라이언트가 지정해야 하므로 쓰기 허용
        read_only_fields = ['id', 'author', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    """게시글 목록/상세용. 댓글은 개수만 노출(가벼운 응답)."""

    author = serializers.ReadOnlyField(source='author.username')
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'comment_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def get_comment_count(self, obj):
        return obj.comments.count()


class PostDetailSerializer(PostSerializer):
    """게시글 상세 조회용. 댓글 목록까지 중첩(nested)해서 함께 반환."""

    comments = CommentSerializer(many=True, read_only=True)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']
