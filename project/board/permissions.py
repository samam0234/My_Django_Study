from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """읽기는 누구나, 쓰기(수정/삭제)는 작성자 본인만 허용하는 객체 단위 퍼미션."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
