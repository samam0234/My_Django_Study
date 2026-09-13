from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register('posts', api_views.PostViewSet, basename='api_post')
router.register('comments', api_views.CommentViewSet, basename='api_comment')

urlpatterns = router.urls
