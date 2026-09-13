# studyFinal. 지금까지 배운 것을 응용한 미니 웹사이트 프로젝트

`study0.md` ~ `study10.md`에서 하나씩 익힌 내용을 **하나의 완결된 프로젝트**(`project/`)로 종합합니다. `demo/`가 "개념별로 하나씩 실습해보는 누적 프로젝트"였다면, `project/`는 "처음부터 다시 설계해서 완성한 결과물"입니다.

## 1. 프로젝트 한 줄 정의

**미니 커뮤니티 게시판**: 회원가입/로그인한 사용자가 게시글과 댓글을 작성할 수 있는 게시판. 같은 기능을 **Django 템플릿 화면**과 **DRF REST API** 두 가지 방식으로 동시에 제공하여, 서버 렌더링 웹앱과 프론트엔드 분리형(React/Vue + API) 아키텍처를 모두 경험할 수 있도록 구성했습니다.

## 2. 기술 스택 및 적용 개념 총정리

| 계층 | 사용 기술/개념 | 관련 문서 |
|---|---|---|
| 프로젝트 구조 | `config`(설정) + `accounts`(회원) + `board`(게시판) | study0, study1 |
| 데이터베이스 | SQLite, 커스텀 `User(AbstractUser)`, `Post`, `Comment` (FK 관계) | study2 |
| 화면(템플릿) | CBV(ListView/DetailView/CreateView/UpdateView/DeleteView), 템플릿 상속 | study3 |
| 인증 | 세션 로그인, `LoginRequiredMixin`, 작성자 전용 권한(`UserPassesTestMixin`) | study4 |
| 관리자 | 커스텀 `UserAdmin`, `PostAdmin` + 댓글 `TabularInline` | study5 |
| API | DRF `ModelViewSet` + `DefaultRouter`, Nested Serializer | study6, study7 |
| API 보안/편의 | `IsOwnerOrReadOnly`, `PageNumberPagination`, 검색/필터/정렬 | study8 |
| API 인증(대안) | JWT (`djangorestframework-simplejwt`) | study9 |
| 프론트엔드 연동 | `django-cors-headers`, React/Vue fetch 예시 | study10 |

## 3. `demo/`와 `project/`의 차이

같은 도메인(회원+게시판)을 다루지만 목적이 다릅니다.

- **`demo/`**: study1~study10 각 문서에 정확히 대응하도록, **기능을 하나씩 추가해나간 과정**을 보여주는 프로젝트. 커밋 히스토리를 따라가면 Django를 배우는 순서 그대로 코드가 진화하는 것을 볼 수 있습니다.
- **`project/`**: 배운 내용을 모두 알고 있다는 전제 하에 **처음부터 완성된 형태로 설계**한 최종 결과물. `demo/`에는 없던 다음 기능이 추가되었습니다.
  - 게시글 목록에 **검색창**(`?q=` 제목/내용 부분 일치 검색)
  - 템플릿 목록에도 API와 마찬가지로 **페이지네이션** 적용 (`ListView.paginate_by`, Django 내장 `Paginator` 사용)
  - **댓글 삭제** 기능(작성자 본인만, `CommentDeleteView`)
  - 루트 경로(`/`) 접속 시 게시판 목록으로 자동 리다이렉트
  - 다듬어진 공통 스타일(`base.html`)과 프로젝트 설명 `README.md`

## 4. 템플릿 목록에 검색 + 페이지네이션 추가하기

API 쪽(study8)에서만 다뤘던 페이지네이션/검색을 템플릿 `ListView`에도 적용했습니다. DRF 없이 **Django 기본 기능만으로** 구현할 수 있습니다.

```python
# board/views.py
from django.conf import settings
from django.db.models import Q
from django.views.generic import ListView


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = settings.BOARD_PAGE_SIZE   # ListView가 내부적으로 Paginator를 사용

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context
```

- `paginate_by` 속성만 지정하면 `ListView`가 자동으로 `Paginator`를 적용하고, 템플릿에 `page_obj`, `is_paginated` 컨텍스트를 넘겨줍니다.
- `Q(title__icontains=query) | Q(content__icontains=query)` : `Q` 객체로 "제목 OR 내용에 포함"이라는 조건을 조합. `icontains`는 대소문자 구분 없는 부분 일치.

```html
<!-- board/templates/board/post_list.html -->
{% if is_paginated %}
<div class="pagination">
    {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}{% if query %}&q={{ query }}{% endif %}">이전</a>
    {% endif %}
    <span>{{ page_obj.number }} / {{ page_obj.paginator.num_pages }} 페이지</span>
    {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}{% if query %}&q={{ query }}{% endif %}">다음</a>
    {% endif %}
</div>
{% endif %}
```

## 5. 프로젝트 구조

```
project/
├── manage.py
├── requirements.txt
├── README.md
├── config/
│   ├── settings.py     # study1~study10 설정을 모두 통합
│   └── urls.py          # '/', '/board/', '/accounts/', '/api/', '/api/token/'
├── accounts/
│   ├── models.py         # User(AbstractUser)
│   ├── forms.py           # SignUpForm
│   ├── views.py            # SignUpView
│   ├── admin.py             # UserAdmin
│   └── templates/accounts/  # signup.html, login.html
├── board/
│   ├── models.py          # Post, Comment
│   ├── views.py            # 템플릿 CBV (검색+페이지네이션 포함)
│   ├── admin.py             # PostAdmin + CommentInline
│   ├── serializers.py        # PostSerializer, PostDetailSerializer, CommentSerializer
│   ├── permissions.py         # IsOwnerOrReadOnly
│   ├── api_views.py            # PostViewSet, CommentViewSet
│   ├── api_urls.py              # DefaultRouter
│   └── templates/board/          # post_list/detail/form/confirm_delete, comment_*
└── templates/
    └── base.html            # 공통 레이아웃 (검색바 스타일, 로그인 상태 네비게이션)
```

## 6. 실습: 최종 프로젝트 구축 및 통합 검증

진행한 작업:

1. `project/.venv` 생성, `django`, `djangorestframework`, `django-filter`, `djangorestframework-simplejwt`, `django-cors-headers` 설치
2. `config`, `accounts`, `board` 프로젝트/앱 생성, `study1~study10` 설정을 하나의 `settings.py`에 통합
3. `accounts`, `board` 모델/템플릿/뷰/Admin/Serializer/ViewSet/Permission 작성 (study2~study9 내용을 모두 반영)
4. **studyFinal 확장**: `PostListView`에 검색(`q`) + 페이지네이션(`paginate_by`) 추가, `CommentDeleteView` 추가, 루트(`/`) 리다이렉트 추가
5. `README.md` 작성 (실행 방법, 경로 목록, 폴더 구조, 확장 아이디어)

### 통합 검증 결과

```text
[템플릿]
GET  /                          → 302 → /board/ 로 리다이렉트
GET  /board/                    → 200, "1 / 2 페이지" (게시글 7개, 페이지당 5개)
GET  /board/?q=number+3         → 200, "Sample Post 3"만 검색됨
로그인 → 댓글 작성 → 댓글 삭제(본인)  → 정상 동작, DB에서 실제로 삭제 확인

[Admin]
POST /admin/login/              → 302 (로그인 성공)
GET  /admin/board/post/         → 200

[API]
POST /api/token/  (alice)                     → 200, access/refresh 토큰 발급
POST /api/posts/  (Bearer 토큰, 세션 없음)      → 201 (JWT만으로 작성 성공)
GET  /api/posts/                               → {"count": 8, ...} (페이지네이션 적용)
GET  /api/posts/ (Origin: localhost:5173)       → access-control-allow-origin 헤더 포함
```

Notion 학습 목표 8개 항목을 모두 반영한 최종 프로젝트가 정상 동작함을 확인했습니다.

## 7. 다음 단계로 나아가려면

`README.md`의 "확장 아이디어" 절에 정리했듯, 이후에는 다음을 시도해볼 수 있습니다.

- 실제 React 또는 Vue 프로젝트를 새로 만들어 `/api/`를 소비하는 SPA 구현 (study10에서 배운 CORS 설정이 여기서 실제로 쓰입니다)
- 좋아요, 태그, 이미지 업로드 등 기능 확장
- `.env` 기반 설정 분리, gunicorn/nginx 또는 클라우드 플랫폼으로 배포

이것으로 Notion의 Django 학습 목표(`study0` ~ `studyFinal`)를 모두 완료했습니다.
