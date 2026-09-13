# study3. 실습3 — 템플릿 뷰(MTV)

Notion 학습 목표 대응: **템플릿 뷰(MTV)**

이번 실습에서는 study2에서 만든 `Post` 모델을 화면(Template)과 연결하여 목록/상세/작성/수정/삭제(CRUD)를 템플릿 기반으로 구현합니다.

## 1. FBV vs CBV

Django의 View는 두 가지 방식으로 작성할 수 있습니다.

- **FBV(Function-Based View)**: 함수로 작성. `study1`의 `hello()`가 예시. 로직이 단순할 때 직관적.
- **CBV(Class-Based View)**: 클래스로 작성. Django가 제공하는 `generic view`(ListView, DetailView, CreateView, UpdateView, DeleteView 등)를 상속하면 CRUD 로직 대부분을 코드 몇 줄로 대체 가능.

이번 게시판은 전형적인 CRUD이므로 CBV(Generic View)를 사용합니다.

| Generic View | 역할 | 기본 템플릿 이름 규칙 |
|---|---|---|
| `ListView` | 목록 조회 | `<app>/<model>_list.html` |
| `DetailView` | 단건 조회 | `<app>/<model>_detail.html` |
| `CreateView` | 생성 폼 + 저장 | `<app>/<model>_form.html` |
| `UpdateView` | 수정 폼 + 저장 | `<app>/<model>_form.html` (Create와 공유) |
| `DeleteView` | 삭제 확인 + 삭제 | `<app>/<model>_confirm_delete.html` |

템플릿 파일명 규칙을 따르면 `template_name`을 직접 지정하지 않아도 Django가 자동으로 찾아줍니다.

## 2. URL 패턴과 path converter

```python
# board/urls.py
from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('new/', views.PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
]
```

- `<int:pk>`는 **path converter**입니다. URL의 해당 위치 값을 정수로 변환해 뷰에 `pk` 키워드 인자로 전달합니다. Generic View들은 기본적으로 `pk`(또는 `slug`)로 객체를 조회합니다.
- CBV는 `.as_view()`로 호출해야 실제 view 함수처럼 동작합니다 (클래스를 함수로 변환해주는 역할).

## 3. Generic View 구현

```python
# board/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .models import Post


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'   # 템플릿에서 {{ posts }}로 접근


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'


class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'author']  # 임시: author를 폼에서 직접 선택
    # study4에서 로그인 사용자(request.user)를 자동으로 author로 지정하도록 개선 예정


class PostUpdateView(UpdateView):
    model = Post
    fields = ['title', 'content']


class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('board:post_list')
```

`fields`만 지정하면 Django가 자동으로 `ModelForm`을 만들어줍니다. `reverse_lazy`는 `reverse`와 동일하게 URL 이름 → 실제 경로를 변환하지만, **모듈이 로드되는 시점(URLconf가 아직 준비 안 됐을 수도 있는 클래스 속성 정의 시점)에 지연 평가**되도록 만든 버전입니다. 클래스 속성으로 쓸 때는 항상 `reverse_lazy`를 사용합니다.

> ⚠️ 지금 `PostCreateView`는 `author`를 폼에서 직접 선택하게 되어 있어 로그인 없이도 아무나 다른 사람 이름으로 글을 쓸 수 있는 상태입니다. 이는 회원 인증(study4)을 아직 붙이지 않았기 때문이며, study4에서 `LoginRequiredMixin` + `request.user`로 교체해 해결합니다.

## 4. 템플릿 문법

### 템플릿 상속 (base.html)

공통 레이아웃은 `demo/templates/base.html`에 두고, 각 페이지 템플릿은 이를 상속(`{% extends %}`)합니다.

```html
<!-- templates/base.html -->
<nav>
    <a href="{% url 'board:post_list' %}">게시판</a>
</nav>
{% block content %}{% endblock %}
```

```html
<!-- board/templates/board/post_list.html -->
{% extends 'base.html' %}
{% block content %}
  <h1>게시글 목록</h1>
  {% for post in posts %}
    <a href="{% url 'board:post_detail' post.pk %}">{{ post.title }}</a>
  {% empty %}
    <p>등록된 게시글이 없습니다.</p>
  {% endfor %}
{% endblock %}
```

핵심 문법:

- `{% extends %}` : 부모 템플릿 상속
- `{% block 이름 %}...{% endblock %}` : 자식이 덮어쓸 수 있는 영역
- `{{ 변수 }}` : 값 출력 (자동으로 HTML 이스케이프 처리되어 XSS 방지)
- `{% for %} ... {% empty %} ... {% endfor %}` : 반복문 (빈 목록일 때 `empty` 블록 표시)
- `{% url 'app:name' arg %}` : URL 이름으로 실제 경로를 역참조 (하드코딩 방지)
- `{{ value|filter }}` : 템플릿 필터. 예) `{{ post.created_at|date:'Y-m-d H:i' }}`, `{{ post.content|linebreaks }}`

### 앱 템플릿 디렉터리 규칙

`APP_DIRS = True` 설정 덕분에 Django는 각 앱의 `templates/` 폴더를 자동으로 탐색합니다. 이때 다른 앱과 이름이 겹치지 않도록 **앱 이름으로 한 번 더 감싼 폴더**를 관례로 사용합니다.

```
board/
└── templates/
    └── board/              ← 앱 이름으로 감싸기
        ├── post_list.html
        ├── post_detail.html
        ├── post_form.html
        └── post_confirm_delete.html
```

## 5. Form 렌더링과 CSRF

```html
<!-- board/templates/board/post_form.html -->
{% extends 'base.html' %}
{% block content %}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">저장</button>
</form>
{% endblock %}
```

- `{% csrf_token %}`: Django의 CSRF(Cross-Site Request Forgery) 보호 토큰을 폼에 숨겨진 필드로 삽입합니다. `method="post"` 폼에는 **반드시** 넣어야 하며, 빠뜨리면 403 오류가 발생합니다.
- `{{ form.as_p }}`: CBV가 자동 생성한 `ModelForm`을 `<p>` 태그로 감싸 렌더링. (`as_table`, `as_ul` 등 다른 렌더링 방식도 있음)

## 6. 실습3: board 앱 템플릿 기반 CRUD 구현

진행한 작업:

1. `templates/base.html` 작성 (공통 레이아웃, 메시지 표시 영역)
2. `board/templates/board/` 하위에 `post_list.html`, `post_detail.html`, `post_form.html`, `post_confirm_delete.html` 작성
3. `board/views.py`를 Generic CBV(ListView/DetailView/CreateView/UpdateView/DeleteView)로 전면 교체
4. `board/urls.py`를 CRUD 경로로 재구성 (`study1`의 `hello/` 경로는 제거)
5. 상세 페이지에서 댓글 목록을 읽기 전용으로 표시 (`post.comments.all`, 작성 기능은 study4에서 추가)
6. `config/urls.py`에 루트 경로(`/`) 리다이렉트 추가 — `board:post_list`가 이 시점부터 사실상 사이트의 메인 화면이 되었기 때문

```python
# config/urls.py
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='board:post_list', permanent=False)),
    path('admin/', admin.site.urls),
    path('board/', include('board.urls')),
]
```

> 💡 `path('')`를 추가하기 전에는 `http://127.0.0.1:8000/`(포트만 있고 경로가 없는 루트 주소)로 접속하면 매칭되는 URL 패턴이 없어 **404**가 떴습니다. `RedirectView`로 루트를 `board:post_list`로 보내주면 사용자가 `/board/`를 몰라도 기본 주소만으로 메인 화면(게시글 목록)에 들어올 수 있습니다. `permanent=False`는 브라우저에 "영구 리다이렉트(301)"로 캐싱되지 않도록 하기 위함(개발 중 경로가 바뀔 수 있으므로 302를 사용).

### 동작 확인

```bash
$ curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8001/
302
$ curl -o /dev/null -w "%{http_code}\n" -L http://127.0.0.1:8001/
200
$ curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8001/board/
200
$ curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8001/board/1/
200
$ curl -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8001/board/new/
200
```

목록/상세/작성 페이지가 모두 정상적으로 렌더링됩니다. 다음 문서(study4)에서는 회원가입/로그인/로그아웃을 붙이고, 글쓰기·댓글 작성을 로그인 사용자로 제한합니다.
