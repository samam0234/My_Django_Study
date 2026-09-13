# 미니 커뮤니티 게시판 (studyFinal 프로젝트)

`study0.md` ~ `study10.md`에서 배운 내용을 모두 적용해 만든 완결된 미니 웹사이트입니다. 같은 도메인(회원 + 게시판)을 **템플릿(MTV)** 과 **DRF API** 두 가지 방식으로 동시에 제공합니다.

## 기능 요약

| 영역 | 내용 | 대응 study |
|---|---|---|
| 프로젝트/앱 구조 | `config` 프로젝트 + `accounts`(회원), `board`(게시판) 앱 | study1 |
| 모델 | 커스텀 `User`(닉네임/자기소개), `Post`, `Comment` | study2 |
| 템플릿 뷰 | 게시글 목록/상세/작성/수정/삭제, 댓글 작성/삭제 | study3 |
| 회원 인증 | 회원가입/로그인/로그아웃(세션), 작성자 본인만 수정·삭제 | study4 |
| Admin | 커스텀 User Admin, 댓글 Inline | study5 |
| REST API | `/api/posts/`, `/api/comments/` (ViewSet + Router) | study6, 7 |
| 퍼미션/페이지네이션/검색 | `IsOwnerOrReadOnly`, PageNumberPagination, 검색/필터/정렬 | study8 |
| JWT 인증 | `/api/token/`, `/api/token/refresh/` | study9 |
| CORS | React/Vue 개발 서버(5173/3000)에서 API 호출 허용 | study10 |
| **추가(studyFinal)** | 템플릿 목록에 **검색창 + 페이지네이션**, 댓글 삭제, 홈(`/`) 리다이렉트 | studyFinal |

## 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv .venv
.venv/Scripts/Activate.ps1     # Windows PowerShell

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 마이그레이션
python manage.py migrate

# 4. 관리자 계정 생성
python manage.py createsuperuser

# 5. 개발 서버 실행
python manage.py runserver
```

## 주요 경로

| 경로 | 설명 |
|---|---|
| `/` | 게시판 목록으로 리다이렉트 |
| `/board/` | 게시글 목록 (검색: `?q=키워드`, 페이지: `?page=2`) |
| `/board/<pk>/` | 게시글 상세 + 댓글 |
| `/accounts/signup/`, `/accounts/login/`, `/accounts/logout/` | 회원 인증 |
| `/admin/` | Django 관리자 페이지 |
| `/api/posts/`, `/api/comments/` | DRF API (세션 또는 JWT 인증) |
| `/api/token/`, `/api/token/refresh/` | JWT 토큰 발급/갱신 |

## 폴더 구조

```
project/
├── manage.py
├── requirements.txt
├── config/            # 프로젝트 설정 (settings, urls)
├── accounts/           # 회원 (모델, 폼, 뷰, Admin)
├── board/               # 게시판 (모델, 템플릿 뷰, Admin, DRF serializer/viewset/permission)
└── templates/           # 프로젝트 공통 템플릿 (base.html)
```

## 확장 아이디어 (다음 단계)

- 게시글 좋아요, 태그, 이미지 업로드
- 댓글 대댓글(threaded comment)
- `django-environ` 등으로 설정을 dev/prod 환경별로 분리
- gunicorn + nginx 또는 클라우드(예: Railway, Render)로 배포
- 실제 React/Vue 프로젝트를 붙여 `/api/`를 소비하는 SPA 프론트엔드 구현
