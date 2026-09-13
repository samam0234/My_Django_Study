from django.contrib import admin

from .models import Comment, Post


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
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
