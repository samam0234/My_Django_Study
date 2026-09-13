# study10. 고급 기술 구현 5 — React/Vue와 CORS 연동

Notion 학습 목표 대응: **React / Vue와 CORS 연동**

지금까지 만든 `/api/` 엔드포인트를 실제로 React/Vue 같은 별도의 프론트엔드 프로젝트에서 호출하려면 **CORS(Cross-Origin Resource Sharing)** 설정이 필요합니다. 이번 문서가 이 커리큘럼(study0~study10)의 마지막 "고급 기술" 항목입니다.

## 1. CORS란? 왜 필요한가?

브라우저는 보안을 위해 **동일 출처 정책(Same-Origin Policy)**을 따릅니다. 웹 페이지가 자신과 다른 origin(프로토콜+도메인+포트 조합)으로 요청을 보내는 것을 기본적으로 차단합니다.

```
Django API 서버:     http://127.0.0.1:8000
React 개발 서버:      http://localhost:3000   ← origin이 다름 (포트가 다름)
Vue(Vite) 개발 서버:  http://localhost:5173   ← origin이 다름
```

React/Vue 개발 서버(다른 포트)에서 Django API(`/api/posts/` 등)를 `fetch`로 호출하면, 브라우저가 응답을 받고도 "CORS 정책 위반"으로 자바스크립트에서 접근을 차단합니다. 서버가 "이 origin의 요청은 허용한다"고 명시적으로 응답 헤더에 표시해야 브라우저가 허용합니다.

## 2. django-cors-headers 설치 및 설정

```bash
pip install django-cors-headers
```

```python
# config/settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # ⚠️ CommonMiddleware보다 반드시 위(먼저)에 위치
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',   # Vite(React/Vue) 개발 서버 기본 포트
    'http://127.0.0.1:5173',
    'http://localhost:3000',   # Create React App 등
    'http://127.0.0.1:3000',
]
CORS_ALLOW_CREDENTIALS = True  # 세션 쿠키를 포함한 요청(withCredentials)을 허용
```

- `CorsMiddleware`의 위치가 중요합니다. Django 공식 문서 권장대로 **가능한 한 위쪽**(특히 응답에 헤더를 추가하는 `CommonMiddleware`보다 앞)에 둬야 모든 응답에 CORS 헤더가 정상적으로 붙습니다.
- `CORS_ALLOWED_ORIGINS`: 화이트리스트 방식으로 허용할 origin을 명시합니다. (전체 허용은 `CORS_ALLOW_ALL_ORIGINS = True`로 가능하지만, 자격 증명(쿠키)을 함께 쓸 때는 보안상 권장되지 않습니다.)
- `CORS_ALLOW_CREDENTIALS`: 세션 인증(쿠키)을 쓰는 요청까지 허용할지 여부. JWT만 쓴다면 꼭 필요하진 않지만, 이 프로젝트는 세션도 함께 지원하므로 켜둡니다.

### 동작 확인

```bash
$ curl -D - -o /dev/null -H "Origin: http://localhost:5173" http://127.0.0.1:8000/api/posts/
access-control-allow-origin: http://localhost:5173
access-control-allow-credentials: true

$ curl -D - -o /dev/null -H "Origin: http://evil.com" http://127.0.0.1:8000/api/posts/
(access-control 헤더 없음 → 브라우저가 evil.com에서의 응답 접근을 차단)
```

## 3. React에서 API 호출 예시

```jsx
// React 예시 — JWT 사용 (다른 origin, 쿠키 불필요)
async function fetchPosts() {
  const res = await fetch('http://127.0.0.1:8000/api/posts/', {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  const data = await res.json();
  return data.results; // 페이지네이션 응답이므로 results 배열을 사용
}

async function login(username, password) {
  const res = await fetch('http://127.0.0.1:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  const { access, refresh } = await res.json();
  localStorage.setItem('access', access);
  localStorage.setItem('refresh', refresh);
}
```

axios를 쓴다면 인터셉터로 토큰을 자동으로 붙이는 방식이 흔합니다.

```js
import axios from 'axios';

const api = axios.create({ baseURL: 'http://127.0.0.1:8000/api/' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

## 4. Vue에서 API 호출 예시

```js
// Vue 3 (Composition API) 예시
import { ref, onMounted } from 'vue';

export function usePosts() {
  const posts = ref([]);

  onMounted(async () => {
    const res = await fetch('http://127.0.0.1:8000/api/posts/');
    const data = await res.json();
    posts.value = data.results;
  });

  return { posts };
}
```

React든 Vue든 핵심은 동일합니다: **Django가 CORS를 허용한 origin에서, JWT(`Authorization` 헤더) 또는 세션 쿠키(`credentials: 'include'`)로 인증하여 `/api/`를 호출**하는 구조입니다.

## 5. 환경별 설정 분리에 대한 참고

지금은 학습용으로 `settings.py` 하나에 모든 설정을 두었지만, 실제 배포에서는 보통 아래처럼 나눕니다.

- 개발(dev): `DEBUG=True`, `CORS_ALLOWED_ORIGINS`에 localhost 포트들
- 운영(prod): `DEBUG=False`, `ALLOWED_HOSTS`에 실제 도메인, `CORS_ALLOWED_ORIGINS`에 실제 프론트엔드 배포 도메인만 등록, `SECRET_KEY`/DB 접속정보 등은 환경변수(`.env`)로 분리

이 커리큘럼에서는 개념만 짚고 넘어가며, 구체적인 배포 구성은 이번 스코프 밖입니다.

## 6. 실습: django-cors-headers 적용

진행한 작업:

1. `pip install django-cors-headers`
2. `INSTALLED_APPS`에 `corsheaders` 추가
3. `MIDDLEWARE`에 `CorsMiddleware`를 `CommonMiddleware`보다 앞에 추가
4. `CORS_ALLOWED_ORIGINS`(Vite/CRA 개발 포트), `CORS_ALLOW_CREDENTIALS = True` 설정
5. `curl -H "Origin: ..."`으로 허용/비허용 origin에 대한 응답 헤더 차이 확인

### 검증 결과

```text
Origin: http://localhost:5173  → access-control-allow-origin 헤더 포함 (허용)
Origin: http://evil.com        → 헤더 없음 (차단)
```

이것으로 Notion 학습 목표 8개 항목(프로젝트/앱/설정, 모델+마이그레이션, 템플릿뷰, DRF API, 시리얼라이저/퍼미션/페이지네이션, 세션 vs JWT, Admin 커스터마이징, React/Vue와 CORS 연동)을 모두 실습했습니다. 마지막으로 `studyFinal.md`에서 지금까지 배운 내용을 하나의 완결된 미니 웹사이트 프로젝트(`project/`)로 종합합니다.
