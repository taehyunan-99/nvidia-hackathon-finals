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
- score.py, validate.py, test_*.py — 검증
- sync-agents-md.sh, sync_guides.py, guide-pairs.json — both

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
기본 명령은 read-only/dry-run으로 유지한다. 네트워크/쓰기 모드를 명시하고 단위 테스트와 임시 폴더에서 실패 조건을 확인한다.

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
