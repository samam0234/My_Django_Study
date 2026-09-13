# 에이전트 공통 가이드라인 (인수인계 문서)

이 문서는 이 저장소에서 작업하는 모든 AI 에이전트(Claude, Grok, Codex 등)가 **공통으로** 지켜야 할 규칙을 정리한 인수인계 문서입니다.
`.claude/`, `.grok/`, `.codex/` 폴더의 에이전트별 문서는 이 문서를 기본으로 삼고, 도구별 특이사항만 추가로 기술합니다.

## 1. 저장소 개요

- Python [Reflex](https://reflex.dev) 학습 기록 저장소입니다. Reflex는 Python 코드만으로 UI + 상태 + 이벤트를 다루는 프레임워크로, 내부적으로 Python 코드를 컴파일해 React(Next.js) 프론트엔드를 생성합니다.
- 이 저장소는 [../vue.js](../vue.js), [../react](../react) 학습을 마친 상태를 전제로, **Vue/React와 다른 점, 같은 점 위주로** 정리합니다.
- `study0.md`, `study1.md`, `study2.md`, ... 순서로 학습 진도가 진행됩니다. (숫자가 클수록 최신 진도)
  - `study0`: 실습 없이 이론만 (React 기초 이론 — Reflex가 내부적으로 React로 컴파일되기 때문에 선행 지식으로 필요)
  - `study1` ~ `study5`: Reflex 기본기 실습 (프로젝트 생성, State, 이벤트/CRUD, 컴포넌트 분리, 라우팅)
  - `study6` ~ `study10`: 고급 기술 구현 (FastAPI 연동, DB 연동, 인증 상태, 배포 준비, Docker/클라우드 배포)
  - `studyFinal`: 지금까지 배운 것을 합쳐 만드는 미니 게시판 웹사이트
- `demo/`: study1~study5 문서 내용을 개념별로 하나씩 실습하는 Reflex 프로젝트입니다. 실습 컴포넌트/페이지가 계속 누적되는 구조입니다.
- `project/`: `studyFinal.md`에 대응하는, `demo/`에서 익힌 개념을 전부 합쳐 만든 완결된 미니 웹사이트(별도 Reflex 프로젝트)입니다.

## 2. 작업 전 확인 사항

- 새 작업을 시작하기 전에 `studyN.md` 파일들을 번호 순서대로 확인하여 지금까지의 학습 진도와 맥락을 파악합니다.
- `demo/` 프로젝트 코드가 study 문서 설명과 어긋나지 않는지 확인합니다.
- 새 studyN.md 문서를 추가/수정할 때는 이전 study 문서와 이어지는 흐름을 유지합니다.
- Reflex 프로젝트(`demo/`, `project/`)는 각자 독립된 가상환경/`requirements.txt`를 가집니다. 루트의 `.venv`는 문서 작성 중 코드를 검증하기 위한 용도이며 커밋 대상이 아닙니다.

## 3. 커밋 규칙

- 커밋 관련 규칙은 [COMMIT_GUIDE.md](./COMMIT_GUIDE.md) 문서를 따릅니다.

## 4. 언어 규칙

- 문서 내용, 커밋 설명: 한글
- 커밋 타입(prefix), 코드, 식별자, 파일명: 영어

## 5. 에이전트별 문서

- Claude: [.claude/CLAUDE.md](../.claude/CLAUDE.md)
- Grok: [.grok/GROK.md](../.grok/GROK.md)
- Codex: [.codex/AGENTS.md](../.codex/AGENTS.md)

## 6. 인수인계 원칙

- 작업을 마칠 때는 다음 에이전트/세션이 이어받을 수 있도록 변경 내용과 다음 단계 후보를 간단히 남깁니다.
- 불확실한 결정은 추측하지 말고 study 문서 내용과 [Notion 학습 목표 페이지](https://app.notion.com/p/Python-Reflex-3d6d7dec5e2e817a836dd23576cb2e1e)를 근거로 삼습니다.
- 이 문서나 커밋 가이드에 없는 새로운 컨벤션이 필요해지면, 추측해서 각자 다르게 처리하지 말고 이 문서를 먼저 갱신합니다.
