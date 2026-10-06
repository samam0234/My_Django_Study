# Django 학습 저장소

Python 풀스택 웹 프레임워크 **Django**를 이론 → 실습 → 고급 기술 → 최종 프로젝트 순서로 정리한 학습 기록입니다.
학습 목표와 로드맵은 [Notion: Django](https://app.notion.com/p/Django-3d6d7dec5e2e8126ae99e088a23fa314) 페이지를 기준으로 합니다.

공통 주제는 **게시판 + 회원**입니다. 처음에는 Django 템플릿(MTV)으로 만들고, 뒤로 갈수록 DRF(Django REST Framework) API로 확장합니다.

## 학습 진도

| 문서 | 내용 | Notion 학습 목표 |
|---|---|---|
| [study0.md](study0.md) | Django 기초이론 (MTV, 프로젝트/앱, 요청-응답 흐름) | 선행 이론 |
| [study1.md](study1.md) | 설치, 프로젝트/앱 생성 명령어, 실습1 | 프로젝트 / 앱 / 설정 |
| [study2.md](study2.md) | 커스텀 User, Post/Comment 모델, 마이그레이션 | 모델 + 마이그레이션 |
| [study3.md](study3.md) | 클래스형 뷰와 템플릿으로 게시글 CRUD | 템플릿 뷰 (MTV) |
| [study4.md](study4.md) | 회원가입/로그인/로그아웃, 작성자 권한 | 세션 로그인 |
| [study5.md](study5.md) | ModelAdmin, Inline, 커스텀 UserAdmin | Admin 커스터마이징 |
| [study6.md](study6.md) | DRF 시작, Serializer, APIView | DRF로 API |
| [study7.md](study7.md) | ViewSet, Router, Nested Serializer | 시리얼라이저 |
| [study8.md](study8.md) | 소유자 퍼미션, 페이지네이션, 검색/필터 | 퍼미션, 페이지네이션 |
| [study9.md](study9.md) | SimpleJWT 인증 | 세션 로그인 vs JWT |
| [study10.md](study10.md) | django-cors-headers, React/Vue 연동 | CORS 연동 |
| [studyFinal.md](studyFinal.md) | 배운 내용을 합친 미니 커뮤니티 게시판 | 종합 |

## 폴더 구조

```
.
├── study0.md ~ study10.md, studyFinal.md   # 학습 문서
├── demo/        # study1~10 실습이 단계별로 누적되는 Django 프로젝트
├── project/     # studyFinal: 처음부터 완성형으로 다시 설계한 최종 프로젝트
└── .agent/ .claude/ .codex/ .grok/        # AI 에이전트 인수인계 문서 (커밋 규칙 포함)
```

- `demo/`: 커밋 히스토리를 따라가면 학습 순서대로 코드가 진화하는 과정을 볼 수 있습니다.
- `project/`: 템플릿 화면과 DRF API(세션/JWT 인증, CORS)를 함께 제공하며, 목록 검색/페이지네이션과 댓글 삭제 기능이 추가되어 있습니다. 자세한 내용은 [project/README.md](project/README.md)를 참고하세요.

## 실행 방법

`demo/`, `project/`는 각자 독립된 가상환경을 사용합니다 (`.venv`는 커밋하지 않습니다).

```bash
cd project            # 또는 demo
python -m venv .venv
.venv/Scripts/Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

접속: <http://127.0.0.1:8000/> (게시판 목록으로 자동 이동) · 관리자 `/admin/` · API `/api/posts/`

## 기술 스택

Python 3, Django 5.2, Django REST Framework, django-filter, djangorestframework-simplejwt, django-cors-headers, SQLite

## 커밋 규칙

`type: 한글설명` 형식으로 학습 진도(study 번호)별로 커밋합니다. 자세한 내용은 [.agent/COMMIT_GUIDE.md](.agent/COMMIT_GUIDE.md)를 참고하세요.
