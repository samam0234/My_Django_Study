# Claude 전용 인수인계 문서

공통 규칙은 [../.agent/AGENTS.md](../.agent/AGENTS.md) 및 [../.agent/COMMIT_GUIDE.md](../.agent/COMMIT_GUIDE.md)를 먼저 확인하고 따릅니다.
이 문서에는 Claude를 사용할 때만 해당하는 특이사항을 기록합니다.

## Claude 관련 참고 사항

- Reflex CLI(`reflex init`, `reflex run` 등) 실행 시 Windows 콘솔 코드페이지 문제로 `UnicodeEncodeError`가 발생할 수 있습니다. `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` 환경변수를 설정하고 실행하면 해결됩니다.
- `reflex init`은 프로젝트 폴더에 자체적으로 `AGENTS.md`/`CLAUDE.md`를 생성합니다. 이 저장소의 인수인계 문서(`.agent/`, `.claude/` 등)와는 목적이 다르므로(전자는 "이 Reflex 앱을 건드릴 때 참고할 프레임워크 팁", 후자는 "이 학습 저장소 전체의 진행 규칙") 혼동하지 않도록 `demo/`, `project/` 생성 시 자동 생성 파일은 정리하고 저장소 공통 문서만 유지합니다.
