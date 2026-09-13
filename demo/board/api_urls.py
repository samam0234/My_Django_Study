from django.urls import path

from . import api_views

urlpatterns = [
    path('posts/', api_views.PostListAPIView.as_view(), name='api_post_list'),
    path('posts/<int:pk>/', api_views.PostDetailAPIView.as_view(), name='api_post_detail'),
]
