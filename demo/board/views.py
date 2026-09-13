from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .models import Post


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'


class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'author']  # author 직접 선택은 임시 구현.
    # study4에서 로그인 사용자(request.user)를 자동으로 author로 지정하도록 개선합니다.


class PostUpdateView(UpdateView):
    model = Post
    fields = ['title', 'content']


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('board:post_list')
