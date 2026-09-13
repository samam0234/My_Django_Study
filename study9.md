# study9. 고급 기술 구현 4 — 세션 로그인 vs JWT

Notion 학습 목표 대응: **세션 로그인 vs JWT** 중 JWT 부분 (세션 로그인은 study4에서 구현)

## 1. 세션 인증 vs 토큰(JWT) 인증

| 구분 | 세션 인증 (study4, study6~8) | JWT 인증 (이번 문서) |
|---|---|---|
| 상태 저장 위치 | 서버(세션 저장소) + 브라우저 쿠키 | 클라이언트가 토큰을 직접 보관 (localStorage 등) |
| 서버 상태 | Stateful (서버가 세션을 기억) | Stateless (서버는 아무것도 저장하지 않음, 토큰 자체가 정보를 담음) |
| CSRF 방어 필요 여부 | 필요 (쿠키 자동 전송 때문) | 불필요 (매 요청마다 명시적으로 헤더에 토큰을 담아 보내야 하므로) |
| 적합한 상황 | 같은 도메인의 서버 렌더링 템플릿, Admin | SPA(React/Vue), 모바일 앱처럼 **다른 도메인/오리진**에서 API를 호출하는 경우 |
| 만료/무효화 | 서버에서 세션을 즉시 삭제 가능 | Access Token은 만료 전까지 유효 (즉시 무효화가 어려움 → 만료 시간을 짧게 유지) |

이 프로젝트는 "템플릿 버전은 세션, API 버전은 JWT"를 함께 지원하도록 두 인증 방식을 **동시에** 활성화합니다.

## 2. djangorestframework-simplejwt 설치 및 설정

```bash
pip install djangorestframework-simplejwt
```

```python
# config/settings.py
from datetime import timedelta

REST_FRAMEWORK = {
    ...
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',        # 기존 세션(브라우저) 인증 유지
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT 인증 추가
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,  # refresh 요청마다 refresh 토큰도 새로 발급 (탈취 위험 감소)
}
```

`DEFAULT_AUTHENTICATION_CLASSES`에 여러 개를 등록하면, DRF는 **순서대로 시도**해서 먼저 성공하는 인증 방식을 사용합니다. 세션 쿠키가 있으면 세션으로, `Authorization: Bearer <token>` 헤더가 있으면 JWT로 인증됩니다.

## 3. 토큰 발급/갱신 엔드포인트

SimpleJWT는 로그인(토큰 발급)과 갱신용 View를 기본 제공합니다.

```python
# config/urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    ...
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

| 엔드포인트 | 역할 |
|---|---|
| `POST /api/token/` | username/password로 로그인 → `access`, `refresh` 토큰 한 쌍 발급 |
| `POST /api/token/refresh/` | 만료된 `access` 토큰을 `refresh` 토큰으로 재발급 |

## 4. 토큰 구조 (Access / Refresh)

- **Access Token**: 실제 API 요청 시 `Authorization: Bearer <access>` 헤더로 사용. 수명이 짧음(여기서는 30분) — 탈취당해도 피해 범위를 제한하기 위함.
- **Refresh Token**: Access Token이 만료됐을 때 재발급받는 용도. 수명이 김(여기서는 7일). 이것도 탈취되면 위험하므로, 프론트엔드에서는 보통 `httpOnly` 쿠키 등 더 안전한 저장 방식을 권장합니다(이 커리큘럼에서는 기본 흐름 이해에 집중).
- JWT는 헤더/페이로드/서명 3부분으로 이루어진 문자열입니다. 페이로드에는 `user_id`, `exp`(만료시각), `token_type` 등이 인코딩되어 있고(암호화가 아니라 **인코딩**이므로 내용은 디코딩하면 누구나 볼 수 있지만, 서버의 `SECRET_KEY`로 서명되어 있어 변조는 불가능).

## 5. 실습: JWT 로그인 API + 인증 요청 테스트

진행한 작업:

1. `pip install djangorestframework-simplejwt`
2. `config/settings.py` — `SIMPLE_JWT`, `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` 추가
3. `config/urls.py` — `/api/token/`, `/api/token/refresh/` 라우팅 추가

### 검증 결과 (curl)

```bash
# 1. 로그인 → 토큰 발급
$ curl -X POST -H "Content-Type: application/json" \
    -d '{"username":"bob","password":"..."}' \
    http://127.0.0.1:8000/api/token/
{"refresh": "eyJhbGciOi...", "access": "eyJhbGciOi..."}

# 2. Bearer 토큰으로 글 작성 — 세션 쿠키도, CSRF 토큰도 없이 성공
$ curl -H "Authorization: Bearer <access>" -H "Content-Type: application/json" \
    -d '{"title":"JWT post","content":"created without session/csrf"}' \
    http://127.0.0.1:8000/api/posts/
→ 201 {"id":6, "title":"JWT post", "author":"bob", ...}

# 3. refresh 토큰으로 access 토큰 재발급
$ curl -X POST -H "Content-Type: application/json" \
    -d '{"refresh":"<refresh>"}' http://127.0.0.1:8000/api/token/refresh/
→ 200 {"access": "새로운 access 토큰"}

# 4. 잘못된 비밀번호
$ curl -X POST -d '{"username":"bob","password":"wrong"}' http://127.0.0.1:8000/api/token/
→ 401 Unauthorized
```

세션과 달리 **쿠키/CSRF 토큰 없이** `Authorization` 헤더만으로 인증된 요청이 가능함을 확인했습니다. 이는 다음 문서(study10)에서 다룰 "다른 도메인의 프론트엔드(React/Vue)에서 API를 호출하는 상황"에 특히 적합한 방식입니다.

> 💡 참고: 세션 인증(`SessionAuthentication`)을 `DEFAULT_AUTHENTICATION_CLASSES`에서 완전히 제거하지 않고 남겨둔 이유는, Django Admin과 브라우저에서 API를 직접 탐색하는 DRF의 "Browsable API" 화면이 세션 로그인을 필요로 하기 때문입니다. 실제 배포 시에는 API 전용 서버라면 JWT만 남기는 것도 흔한 선택입니다.
