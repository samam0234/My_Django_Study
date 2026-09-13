# study1. 만드는 방법 및 명령어, 실습1

Notion 학습 목표 대응: **프로젝트 / 앱 / 설정**

이 문서부터는 실제로 동작하는 코드를 `demo/` 폴더에 만듭니다. `demo/`는 study1~study10에 걸쳐 계속 기능이 누적되는 하나의 Django 프로젝트입니다.

## 1. 개발 환경 준비

```bash
# demo 프로젝트 전용 가상환경 생성
python -m venv demo/.venv

# 가상환경 활성화 (Windows PowerShell)
demo/.venv/Scripts/Activate.ps1

# Django 설치
pip install django

# 설치 확인
python -m django --version
```

- 가상환경(`venv`)은 프로젝트마다 독립적인 패키지 공간을 만들어줍니다. `demo/`와 `project/`는 각각 별도의 `.venv`를 가지며, 둘 다 Git에는 커밋하지 않습니다(`.gitignore` 참고).
- 설치한 패키지 목록은 `pip freeze > requirements.txt`로 기록해둡니다.

## 2. 프로젝트 생성 명령어

```bash
# 현재 폴더(demo/)에 config라는 이름의 프로젝트 생성
django-admin startproject config .
```

`.`(현재 디렉터리)을 붙이는 이유: 붙이지 않으면 `config/config/manage.py`처럼 한 단계 더 깊은 폴더가 생깁니다. `.`을 붙이면 `manage.py`가 `demo/` 바로 아래에 생겨 관리가 편합니다.

생성 결과:

```
demo/
├── manage.py
└── config/
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── asgi.py
    └── wsgi.py
```

## 3. 앱 생성 명령어

```bash
python manage.py startapp accounts
python manage.py startapp board
```

이 커리큘럼의 공통 스펙(게시판 + 회원)에 따라 두 개의 앱을 만듭니다.

- `accounts` : 회원가입/로그인/사용자 모델 담당
- `board` : 게시글/댓글 CRUD 담당

## 4. 자주 쓰는 manage.py 명령어 정리

| 명령어 | 설명 |
|---|---|
| `python manage.py runserver` | 개발 서버 실행 (기본 포트 8000) |
| `python manage.py runserver 8001` | 포트 지정 실행 |
| `python manage.py startapp <이름>` | 새 앱 생성 |
| `python manage.py makemigrations` | 모델 변경사항을 마이그레이션 파일로 생성 |
| `python manage.py migrate` | 마이그레이션을 실제 DB에 반영 |
| `python manage.py createsuperuser` | Admin 페이지 접근용 관리자 계정 생성 |
| `python manage.py shell` | Django 환경이 로드된 Python 셸 실행 |
| `python manage.py dbshell` | DB 셸 접속 |
| `python manage.py test` | 테스트 실행 |
| `python manage.py collectstatic` | 배포용 정적 파일을 한 곳으로 모음 |
| `python manage.py showmigrations` | 마이그레이션 적용 상태 확인 |

## 5. settings.py 핵심 항목

`config/settings.py`에서 눈여겨봐야 할 항목들입니다.

```python
INSTALLED_APPS = [
    'django.contrib.admin',       # 관리자 페이지
    'django.contrib.auth',        # 인증 시스템
    'django.contrib.contenttypes',
    'django.contrib.sessions',    # 세션 프레임워크
    'django.contrib.messages',    # 플래시 메시지
    'django.contrib.staticfiles', # 정적 파일 관리
    # 우리가 만든 앱은 여기 등록해야 인식됨
    'accounts',
    'board',
]
```

- **INSTALLED_APPS**: 앱을 만들었다고 자동으로 인식되지 않습니다. 반드시 여기에 등록해야 migrations, admin, templates 탐색 대상이 됩니다.
- **DATABASES**: 기본값은 SQLite (`db.sqlite3`). 별도 설정 없이 바로 개발 가능.
- **TEMPLATES / DIRS**: 프로젝트 공통 템플릿 폴더 경로. `BASE_DIR / 'templates'`를 추가해두면 앱에 종속되지 않는 공통 템플릿(`base.html` 등)을 둘 수 있습니다.
- **LANGUAGE_CODE / TIME_ZONE**: 한국어 서비스이므로 각각 `'ko-kr'`, `'Asia/Seoul'`로 설정합니다.
- **ALLOWED_HOSTS**: 배포 환경에서 허용할 호스트 목록. 개발 중엔 `['localhost', '127.0.0.1']` 정도면 충분합니다.

## 6. urls.py 라우팅 기초

Django는 URL 라우팅을 계층적으로 구성합니다. 프로젝트의 최상위 `urls.py`가 앱별 `urls.py`를 `include()`로 위임하는 구조가 일반적입니다.

```python
# config/urls.py (최상위)
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('board/', include('board.urls')),
]
```

```python
# board/urls.py (앱 전용)
from django.urls import path
from . import views

app_name = 'board'  # 네임스페이스: {% url 'board:hello' %} 형태로 참조 가능

urlpatterns = [
    path('hello/', views.hello, name='hello'),
]
```

- `app_name`을 지정해두면 템플릿에서 `{% url 'board:hello' %}`처럼 앱을 구분해서 URL을 역참조할 수 있어, 나중에 URL 경로가 바뀌어도 템플릿 코드를 고칠 필요가 없습니다.

## 7. 실습1: 프로젝트/앱 생성 + 첫 화면 띄우기

`demo/` 폴더에서 진행한 실습 내용입니다.

1. `demo/.venv` 가상환경 생성 후 Django 설치
2. `django-admin startproject config .` 로 프로젝트 생성
3. `accounts`, `board` 앱 생성 후 `INSTALLED_APPS`에 등록
4. `settings.py`에서 `LANGUAGE_CODE`, `TIME_ZONE`, `TEMPLATES.DIRS`, `ALLOWED_HOSTS` 조정
5. `board/views.py`에 간단한 `hello` 뷰 작성:

   ```python
   from django.http import HttpResponse

   def hello(request):
       return HttpResponse("<h1>Hello, Django!</h1><p>board 앱이 정상적으로 연결되었습니다.</p>")
   ```

6. `board/urls.py` 작성 후 `config/urls.py`에 `include('board.urls')`로 연결
7. `python manage.py migrate` 로 초기 테이블(admin/auth/sessions 등) 생성
8. `python manage.py runserver` 실행 후 `http://127.0.0.1:8000/board/hello/` 접속하여 확인

### 확인 결과

```bash
$ curl http://127.0.0.1:8001/board/hello/
<h1>Hello, Django!</h1><p>board 앱이 정상적으로 연결되었습니다.</p>
```

정상적으로 응답이 오는 것을 확인했습니다. 다음 문서(study2)부터는 `accounts`, `board`의 실제 데이터 모델을 설계합니다.
