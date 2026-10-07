# 행사·운영 작업 가이드

## 1. WHAT — 역할
공식 행사 안내와 미확정 규정, 준비 항목·저장소 운영 방법을 관리한다. 합의한 운영 방향과 미확정 시간표·규정을 구분한다.

## 2. CONTENTS — 파일과 기술
- event.md — 사용자 전달 안내
- mission.md — 본선 문화 미션·OpenShell·공통 테스트·17:20 제출·공식 배점
- ../../.agents/skills/submission-check/ — 필수 요건·데모·제출 상태의 반복 점검
- workflow.md — 공동 주제·문서·계약 정리, 단계별 분담·통합·발표 준비 시간표
- guide-sync.md — AGENTS 원본·CLAUDE 참조와 learn 스킬 사본 동기화
- repo-skills.md — repo 작업 스킬 사용법
- ci-policy.md — 변경 영향·검사 시간 예산·미완료 검사 처리 원칙

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
공식 안내는 출처/날짜와 함께 갱신한다. 사용 절차와 실행 조건을 관리하고 별도의 작업 완료 보고는 작성하지 않는다.

## 4. HOW NOT — 주의할 함정
<!-- prev: 지급 여부/한도 미확인 → 2026-10-07 행사 문서의 $500 등록 확인과 실제 계정 가용량을 구분. -->
- Brev 홍보 자원을 현재 계정 가용량으로 확정하지 않는다 — $500 등록 확인 기록과 실제 잔액·계정 한도·가용 인스턴스는 별도다.

## 5. WHERE — 의존성과 경계
제품 범위는 ../product/README.md, AWS/Brev 연결은 ../playbooks/aws-brev-deployment.md에서 관리한다. 모든 미션은 행사 조건에 의존한다. scripts의 검사 결과만 실행 사실로 기록한다.

## 6. WHY — 배경
개발 시간은 10:30–17:30의 7시간이며 주제는 당일 공개된다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_
