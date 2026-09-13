# study0. Django 기초이론

> 이 저장소는 [Notion: Django 학습 목표](https://app.notion.com/p/Django-3d6d7dec5e2e8126ae99e088a23fa314) 페이지를 기준으로 진행합니다.
> 최종 목표: **게시판 + 회원** 기능을 가진 웹앱을 "템플릿 방식"으로 먼저 만들고, 이후 "DRF(Django REST Framework) API" 방식으로 다시 만들어보는 것.

## 1. Django란?

Django는 Python으로 작성된 **풀스택 웹 프레임워크**입니다. "배터리 포함(batteries included)" 철학을 가지고 있어서, 웹 서비스에 필요한 대부분의 기능(ORM, 인증, 관리자 페이지, 폼, 보안 미들웨어 등)을 프레임워크 자체가 기본 제공합니다.

- Instagram, Spotify(일부), Pinterest 등 대규모 서비스에서 실제로 사용
- "설정보다 관례(Convention over Configuration)"를 따르는 프로젝트 구조
- 보안(CSRF, XSS, SQL Injection 방어)이 기본으로 내장되어 있음

### 다른 프레임워크와 비교

| 구분 | Django | Flask/FastAPI | Express(Node) |
|---|---|---|---|
| 성격 | 풀스택(all-in-one) | 마이크로 프레임워크 | 마이크로 프레임워크 |
| ORM | 내장 | 없음(직접 선택) | 없음(직접 선택) |
| 관리자 페이지 | 자동 생성(Admin) | 없음 | 없음 |
| 적합한 상황 | 빠르게 완성된 웹앱을 만들 때 | 가볍고 자유로운 구조가 필요할 때 | JS 풀스택 통일이 필요할 때 |

## 2. MTV 패턴

Django는 흔히 아는 MVC(Model-View-Controller)와 비슷하지만 이름과 역할 분담이 다릅니다. Django는 **MTV(Model-Template-View)** 패턴을 사용합니다.

| MVC 용어 | Django(MTV) 용어 | 역할 |
|---|---|---|
| Model | Model | 데이터베이스 구조 정의, 데이터 다루는 로직 |
| View(화면) | Template | 사용자에게 보여지는 HTML |
| Controller | View | 요청을 받아 Model을 조회/수정하고 Template에 데이터를 넘겨줌 |
| (URL 매핑) | URLconf(urls.py) | 요청 URL과 View를 연결 |

즉, Django에서 "View"는 화면이 아니라 **요청을 처리하는 로직(Controller에 해당)**이고, 화면 역할은 "Template"이 담당합니다. 이 용어 차이를 헷갈리지 않는 것이 중요합니다.

## 3. 요청-응답 흐름

브라우저가 `GET /board/1/` 같은 요청을 보냈을 때 Django 내부에서 일어나는 흐름입니다.

```
[브라우저]
   │  1. HTTP 요청 (GET /board/1/)
   ▼
[WSGI/ASGI 서버] (개발 중에는 runserver가 대신함)
   ▼
[urls.py] : URL 패턴과 일치하는 View를 탐색
   ▼
[views.py] : 요청 처리
   │   - models.py를 통해 DB 조회/저장
   │   - 필요한 데이터를 정리
   ▼
[templates/*.html] : View가 넘겨준 데이터를 HTML로 렌더링
   ▼
[브라우저] ◄── 2. HTTP 응답 (완성된 HTML)
```

DRF(API 서버)로 전환하면 마지막 단계가 "HTML 렌더링" 대신 "JSON 직렬화(Serializer)"로 바뀔 뿐, 전체 흐름(URL → View → Model)은 동일합니다.

## 4. WSGI / ASGI

- **WSGI(Web Server Gateway Interface)**: Python 웹앱과 웹서버 사이의 표준 인터페이스. 동기(sync) 처리 기반. Django는 오랫동안 WSGI만 지원했습니다.
- **ASGI(Asynchronous Server Gateway Interface)**: WSGI의 비동기 버전. WebSocket, 비동기 view 등을 지원하려면 필요합니다. Django 3.0+부터 지원.
- 이 커리큘럼에서는 기본값인 WSGI + `runserver`로 충분합니다. (실무 배포 시에는 gunicorn/uvicorn 같은 WSGI/ASGI 서버 뒤에 Django를 둡니다.)

## 5. 프로젝트 vs 앱 (Project vs App)

Django의 독특한 개념 중 하나입니다.

- **Project**: 하나의 웹사이트 전체. 설정(settings.py), 최상위 URL 라우팅을 가짐.
- **App**: Project 안에서 하나의 기능 단위(모듈). 예: `accounts`(회원), `board`(게시판).
  - 하나의 Project는 여러 App으로 구성됨
  - App은 이론상 다른 Project에도 재사용 가능하도록 설계하는 것이 권장됨

이 커리큘럼에서는 `config`라는 Project 안에 `accounts`, `board` 두 개의 App을 만듭니다.

## 6. Django 프로젝트의 핵심 구성 요소

`django-admin startproject config .` 실행 시 생성되는 구조를 기준으로 설명합니다.

```
config/
├── manage.py            # 명령어 실행 진입점 (runserver, migrate 등)
└── config/
    ├── __init__.py
    ├── settings.py       # 프로젝트 전역 설정
    ├── urls.py            # 최상위 URL 라우팅
    ├── asgi.py            # ASGI 진입점 (비동기 배포용)
    └── wsgi.py            # WSGI 진입점 (동기 배포용)
```

앱을 추가하면(`python manage.py startapp board`) 아래 구조가 생깁니다.

```
board/
├── migrations/        # DB 스키마 변경 이력
├── admin.py           # Admin 페이지에 모델 등록
├── apps.py            # 앱 설정 클래스
├── models.py          # 데이터베이스 모델(테이블) 정의
├── tests.py           # 테스트 코드
└── views.py           # 요청 처리 로직
```

각 파일의 역할:

- **settings.py**: `INSTALLED_APPS`(설치된 앱 목록), `DATABASES`(DB 연결 정보), `TEMPLATES`(템플릿 검색 경로), `MIDDLEWARE`(요청/응답 중간 처리기) 등을 정의
- **urls.py**: URL 패턴 → View 함수/클래스 매핑. `include()`로 앱별 urls.py를 계층적으로 연결 가능
- **models.py**: Python 클래스로 DB 테이블 정의 (ORM)
- **views.py**: 실제 요청 처리 로직 (함수형 FBV 또는 클래스형 CBV)
- **admin.py**: 모델을 Django 기본 관리자 페이지(`/admin/`)에 노출
- **migrations/**: `models.py` 변경 사항을 실제 DB 스키마에 반영하기 위한 변경 이력 파일들

## 7. 개발 환경 준비 개념

- **가상환경(venv)**: 프로젝트마다 독립된 Python 패키지 공간을 만들어 버전 충돌을 방지. `python -m venv .venv`로 생성.
- **pip**: 패키지 설치 도구. `pip install django`로 Django 설치.
- **requirements.txt**: 프로젝트에 필요한 패키지 목록을 기록해두는 파일. `pip freeze > requirements.txt`로 생성, `pip install -r requirements.txt`로 복원.

## 8. 이 커리큘럼의 로드맵

Notion 학습 목표를 아래와 같이 study 문서에 매핑했습니다.

| study 문서 | Notion 학습 목표 | 내용 |
|---|---|---|
| study0 | (선행 이론) | Django 기초이론 |
| study1 | 프로젝트 / 앱 / 설정 | 설치, 프로젝트/앱 생성 명령어, 실습1 |
| study2 | 모델 + 마이그레이션 | 회원/게시판 모델 설계, 실습2 |
| study3 | 템플릿 뷰(MTV) | 게시판 CRUD 템플릿 구현, 실습3 |
| study4 | 세션 로그인(회원) | 회원가입/로그인/로그아웃, 권한 체크, 실습4 |
| study5 | Admin 커스터마이징 | Admin 페이지 커스터마이징, 실습5 |
| study6 | DRF로 API | DRF 시작, Serializer, APIView |
| study7 | 시리얼라이저 심화 | ViewSet, Router, Nested Serializer |
| study8 | 퍼미션, 페이지네이션 | 커스텀 퍼미션, 페이지네이션, 필터링 |
| study9 | 세션 vs JWT | JWT 인증(SimpleJWT) |
| study10 | React/Vue와 CORS 연동 | django-cors-headers, 프론트엔드 연동 |
| studyFinal | (종합) | 지금까지 배운 것으로 미니 웹사이트 프로젝트 |

공통 스펙: **게시판(board) + 회원(accounts)** 도메인을 처음부터 끝까지 사용합니다. 프론트엔드는 처음엔 Django 템플릿, 뒤로 갈수록 DRF API로 전환합니다.

## 9. 실습 프로젝트 구조 예고

이번 커리큘럼은 문서(이론)뿐 아니라 실제로 동작하는 코드도 함께 작성합니다.

- `demo/` : study1~study10 실습 내용이 단계별로 누적되는 Django 프로젝트
- `project/` : studyFinal에서 만드는, 지금까지 배운 내용을 총정리한 완결된 미니 웹사이트

다음 문서(study1)부터 실제로 손을 움직여 프로젝트를 만들어봅니다.
