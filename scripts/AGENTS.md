# 준비·검증 도구 작업 가이드

## 1. WHAT — 역할
<!-- prev: 오프라인 검색/평가/분류·스킬 확보·모델 probe·sync 중심 → 2026-10-07 update 사용자 확인으로 연결 시험·보안 하네스·수동 배포까지 역할 반영. -->
준비·검증·연결 시험·수동 배포 도구를 관리한다. 오프라인 검색/평가/분류, 스킬 확보, 자료·모델 probe, OpenShell 보안 하네스, AWS–Brev 시험 API와 프런트 배포, 가이드 sync를 포함한다. 제품 에이전트 통합 완료를 뜻하지 않는다.

## 2. CONTENTS — 파일과 기술
- lookup.py — metadata 검색
- model_policy.py, test_model_policy.py — 공통 모델 예산·재시도·일일 누적
- rehearsal.py, test_rehearsal.py — 합성 도구·mock 판단·계약/검색 경로 검증
- classify_skills.py, refresh_catalog.py — 분류/공식 index
- fetch_skill.py — 고정 원문 확보
- probe_nim.py, probe_research.py, preflight.py — 연결/환경 점검
- probe_family_sources.py, test_probe_family_sources.py — 서울 예약 API·공식 상세 자료의 개발 호스트 조회와 키 비노출 검사
- openshell_harness/, test_openshell*.py — 모델 없는 합성 파일·네트워크 경계와 안전한 결과 회수 검사
- bridge_api.py, bridge/, bridge_boundary.py, bridge_check.py, bridge_recovery_check.py, test_bridge_api.py — AWS–Brev의 모델 없는 작업 전달·권한·복구 연결 시험
- deploy_frontend.py — 기존 AWS의 두루 합성 프런트를 Docker로 수동 배포
- serve_preview.py — 환경 파일을 제외한 로컬 미리보기
- score.py — topic-v1·agent-v2/frontend-v2·통합·finals-v1 채점
- validate.py, test_*.py — 링크·인덱스·가이드·동작 검사
- sync-agents-md.sh, sync_guides.py, guide-pairs.json — 가이드 @ 참조 검사·learn 사본의 안전한 동기화

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
<!-- prev: AGENTS/CLAUDE 본문도 양방향 복사 → 2026-10-07 사용자 요청으로 AGENTS 원본·CLAUDE @ 참조를 검사하며 가이드 내용은 복사하지 않음. -->
<!-- prev: 기본 명령 전체를 read-only/dry-run으로 설명 → 2026-10-05 사용자 확인으로 조회·점검과 갱신 명령의 실제 부작용을 구분. -->
<!-- prev: probe 전체를 기본 dry-run으로 설명 → 2026-10-07 update 사용자 확인으로 자료/모델 probe와 실제 경계·운영 도구의 부작용 구분. -->
자료·모델 probe의 기본 dry-run을 유지하며, 실제 sandbox 검사·서버·배포는 아래 부작용과 연결된 사용법을 확인한다. 실행·자원 변경·모델/API 호출은 현재 대화에서 승인된 범위와 예산 안에서만 수행한다. 단위 테스트와 임시 폴더에서 실패 조건을 확인한다.

| 명령 | 기본 동작과 부작용 |
|---|---|
| lookup.py, validate.py, preflight.py | 로컬 조회·점검; 데이터·가이드를 갱신하지 않음 |
| probe_nim.py, probe_research.py | 기본 HTTP 0회; --live에서 실제 모델 호출, --output 사용 시 실행 결과 저장 |
| probe_family_sources.py | 기본 HTTP 0회; --live에서 자료 조회, 정식 HTTP 키 전송은 --allow-http-key 명시 필요 |
| openshell_harness/ | 선택한 모드에서 합성 파일 open·임시 output 생성 또는 고정 합성 전송/수신; dry-run으로 간주하지 않음 |
| bridge_api.py, bridge_check.py, bridge_boundary.py, bridge_recovery_check.py | 모델 없는 서버·작업·경계·복구 시험; 실제 sandbox 생성·실행 등 부작용은 연동 사용법 확인 |
| deploy_frontend.py | 프런트 build·원격 전송·컨테이너 교체·CloudFront 반영을 명시적으로 수동 실행 |
| rehearsal.py | 기본 합성 실행·표준 출력; --write-fixtures에서 예시 JSON 재생성 |
| refresh_catalog.py | 기본 GitHub 네트워크 조회; --write에서 로컬 metadata 갱신 |
| classify_skills.py | 실행 즉시 분류 metadata·탐색 문서 재생성; dry-run 없음 |
| fetch_skill.py | 지정 --dest로 네트워크 다운로드·파일 생성; 소프트웨어 실행/설치는 아님 |
| sync-agents-md.sh | --check는 가이드 참조·사본 비교만; 인자 없으면 가이드 참조/index 검사 후 learn 스킬 사본만 staged 방향 동기화·상대 파일 staging |
| serve_preview.py | 로컬 HTTP 서버 시작; 사용 뒤 서버 종료 필요 |

저장소 루트에서 문서·가이드 참조는 `python3.11 scripts/validate.py`와 `bash scripts/sync-agents-md.sh --check`, 동작은 변경 영향에 맞는 `python3.11 -m unittest discover -s scripts -p 'test_*.py'`로 검사한다. 보안 하네스만 바뀌면 패턴을 `'test_openshell*.py'`로 좁힌다. Python 3.11+를 팀 실행 기준으로 사용하며 프런트 검사는 ../frontend/README.md의 Node 명령을 따른다.

## 4. HOW NOT — 주의할 함정
- sync가 unstaged/부분 staged 수정을 덮어쓰면 안 된다 — 팀원 변경을 잃는다.
- probe 기본 실행에서 실모델을 부르지 않는다 — 반복 점검이 호출 예산을 소모한다.

## 5. WHERE — 의존성과 경계
docs/catalog JSON, docs/evaluation JSON, guide-pairs.json을 소비한다. 자료 원본은 ../docs/product/data-sources.md, 모델 한도는 ../docs/playbooks/model-policy.json, 보안 사용법은 ../docs/playbooks/openshell-harness.md, 연결 시험은 ../docs/playbooks/aws-brev-deployment.md, 배포는 ../docs/playbooks/frontend-deployment.md를 따른다. 공개 프런트·bridge·보안 probe의 개별 성공과 제품 통합 성공을 구분한다.

## 6. WHY — 배경
준비 폴더는 Python 표준 라이브러리로 조회 가능해야 한다. refresh만 PyYAML이 추가로 필요하다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_
