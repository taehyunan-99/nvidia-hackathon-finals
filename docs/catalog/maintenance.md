# 카탈로그·분류 유지

## 원본과 자동 생성 경계

- `skills-index.json`: 공식 frontmatter·source SHA·hash와 프로젝트 탐색 분류를 담은 단일 스킬 원본.
- `skills/`: 위 파일에서 만든 도메인/작업별 목록. 직접 편집하지 않는다.
- `classify_skills.py`: 11개 domain과 7개 function의 분류 규칙. 공식 category는 그대로 보존한다. 생명과학·문서·음성 등 사용자 미션에서 중요한 축은 이름/설명과 주요 스킬의 명시 매핑으로 교차 분류했다. 공식 category도 함께 유지한다.
- `tools-index.json`, `agents-index.json`, `recipes-index.json`: 팀이 선별한 실행 경로. 해당 문서 카드와 함께 갱신한다.

## 새 upstream 버전 검토

1. 공식 repository의 새 commit과 변경 내용을 확인한다. `scripts/refresh_catalog.py`의 PINS를 의도한 SHA로 바꾼다.
2. `uv run --no-project --with pyyaml python scripts/refresh_catalog.py`로 쓰기 없이 전체 metadata를 가져올 수 있는지 점검한다.
3. 반영할 때만 같은 명령에 `--write`를 추가한다. 원본 JSON과 분류 뷰를 재생성한다. 변경된 source revision과 설치 대상을 함께 확인한다.
4. `python3 scripts/validate.py`와 unittest를 실행하고 변경된 실제 스킬의 참조/환경/실행법을 검토한다.

분류만 바꿀 때는 `python3 scripts/classify_skills.py`를 실행한다. 테스트가 유지되어도 자동 분류의 의미가 항상 최적이라는 뜻은 아니다. 자주 찾는 미션이 부적절한 domain/function에 들어가면 분류 규칙과 검색 키워드를 함께 조정한다.

## 범위/권리/실행 상태

공식 source URL·revision·license metadata를 보존했다. metadata는 NVIDIA/skills와 NVIDIA/NeMo-Agent-Toolkit 원문에서 추출했고 domain/function과 한국어 설명/조합은 이 프로젝트의 편집이다. 원문 라이선스는 각 entry와 repository 원문을 따른다.
다운로드 helper는 선택한 폴더와 repository 라이선스/NOTICE를 함께 보존한다. 실행 파일 권한도 Git mode에 맞춘다. 수집한 metadata나 라이선스 표기가 모델 가중치·API·데이터의 이용 조건을 대신하지 않는다.

실행 확인은 tool 카드의 상태 또는 별도 run evidence에 남긴다. 새로운 스킬 발견을 이유로 사용 중인 버전을 본선 당일 자동 교체하지 않는다.
