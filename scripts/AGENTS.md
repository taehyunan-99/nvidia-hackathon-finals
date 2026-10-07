# 준비·검증 도구 작업 가이드

## 1. WHAT — 역할
오프라인 검색/평가/분류, 고정 스킬 확보, 선택적 모델 probe와 가이드 sync를 수행한다.

## 2. CONTENTS — 파일과 기술
- lookup.py — metadata 검색
- model_policy.py, test_model_policy.py — 공통 모델 예산·재시도·일일 누적
- rehearsal.py, test_rehearsal.py — 합성 도구·mock 판단·계약/검색 경로 검증
- classify_skills.py, refresh_catalog.py — 분류/공식 index
- fetch_skill.py — 고정 원문 확보
- probe_nim.py, probe_research.py, preflight.py — 연결/환경 점검
- serve_preview.py — 환경 파일을 제외한 로컬 미리보기
- score.py — topic-v1·agent-v2/frontend-v2·통합·finals-v1 채점
- validate.py, test_*.py — 링크·인덱스·가이드·동작 검사
- sync-agents-md.sh, sync_guides.py, guide-pairs.json — 가이드 @ 참조 검사·learn 사본의 안전한 동기화

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
<!-- prev: AGENTS/CLAUDE 본문도 양방향 복사 → 2026-10-07 사용자 요청으로 AGENTS 원본·CLAUDE @ 참조를 검사하며 가이드 내용은 복사하지 않음. -->
<!-- prev: 기본 명령 전체를 read-only/dry-run으로 설명 → 2026-10-05 사용자 확인으로 조회·점검과 갱신 명령의 실제 부작용을 구분. -->
조회·점검은 read-only, probe는 기본 dry-run을 유지한다. 갱신 명령의 네트워크·쓰기·staging은 아래 구분을 확인하고 명시적으로 실행한다. 단위 테스트와 임시 폴더에서 실패 조건을 확인한다.

| 명령 | 기본 동작과 부작용 |
|---|---|
| lookup.py, validate.py, preflight.py | 로컬 조회·점검; 데이터·가이드를 갱신하지 않음 |
| probe_nim.py, probe_research.py | 기본 HTTP 0회; --live에서 실제 모델 호출, --output 사용 시 실행 결과 저장 |
| rehearsal.py | 기본 합성 실행·표준 출력; --write-fixtures에서 예시 JSON 재생성 |
| refresh_catalog.py | 기본 GitHub 네트워크 조회; --write에서 로컬 metadata 갱신 |
| classify_skills.py | 실행 즉시 분류 metadata·탐색 문서 재생성; dry-run 없음 |
| fetch_skill.py | 지정 --dest로 네트워크 다운로드·파일 생성; 소프트웨어 실행/설치는 아님 |
| sync-agents-md.sh | --check는 가이드 참조·사본 비교만; 인자 없으면 가이드 참조/index 검사 후 learn 스킬 사본만 staged 방향 동기화·상대 파일 staging |
| serve_preview.py | 로컬 HTTP 서버 시작; 사용 뒤 서버 종료 필요 |

문서·가이드 참조 확인은 `python3 scripts/validate.py`와 `bash scripts/sync-agents-md.sh --check`, 동작 검사는 변경 영향에 맞는 `python3 -m unittest discover -s scripts -p 'test_*.py'`를 사용한다.

## 4. HOW NOT — 주의할 함정
- sync가 unstaged/부분 staged 수정을 덮어쓰면 안 된다 — 팀원 변경을 잃는다.
- probe 기본 실행에서 실모델을 부르지 않는다 — 반복 점검이 호출 예산을 소모한다.

## 5. WHERE — 의존성과 경계
docs/catalog JSON, docs/evaluation JSON, guide-pairs.json을 소비한다.

## 6. WHY — 배경
준비 폴더는 Python 표준 라이브러리로 조회 가능해야 한다. refresh만 PyYAML이 추가로 필요하다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_
