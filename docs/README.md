# 문서 지도

| 목적 | 진입 |
|---|---|
| 현재 제품·한국 가족 MVP·선택 기능 | [제품 정의](product/README.md) · [에이전트 설계](product/agent-design.md) · [데이터 근거](product/data-sources.md) |
| 공식 상세 미션·100점 배점·17:20 제출 | [본선 미션과 제출 요건](operations/mission.md) |
| 구현 중·제출 전 필수 사항 반복 점검 | [submission-check 스킬](../.agents/skills/submission-check/SKILL.md) |
| 주제 후보 선정·보류·축소 | [주제 선정 기준](evaluation/topic-selection.md) · [선정 근거 분석](evaluation/topic-analysis.md) |
| 도메인/도구/agent/스킬 탐색 | [catalog](catalog/README.md) |
| 한국 문화 미션·OpenShell 필수 조건 | [보안정책·샌드박스 분석](catalog/tools/openshell-security.md) · [외부 사용자 테스트 배포](playbooks/openshell-deployment.md) |
| Brev에 OpenShell 샌드박스 준비 | [호스트 접속·설치·정책 검증·종료](playbooks/brev-openshell-setup.md) |
| AWS 웹/API와 Brev 에이전트 연결 | [배치·인증·통신·복구](playbooks/aws-brev-deployment.md) |
| 조합과 실제 사용 순서 | [playbooks](playbooks/README.md) |
| 프런트/에이전트 입출력 연결 | [계약·schema·fixture](catalog/contracts.md) |
| 도구 선택·분석 과정 화면 | [실행 흐름 컴포넌트](design/agent-flow.md) |
| 검색→계약→화면 점검 | [로컬 리허설](playbooks/rehearsal.md) |
| 2인 분담·통합·로컬 시연 | [운영 기준](operations/workflow.md) |
| 성능·완성도 평가 | [evaluation](evaluation/README.md) |
| 모델 호출 한도·429 복구 | [모델 호출 운영 기준](playbooks/model-policy.md) |
| CI 범위·시간 초과·대체 확인 | [CI 운영 원칙](operations/ci-policy.md) |
| 대회 조건/저장소 운영 | [operations](operations/event.md) |
| 디자인 선택/스킬 | [design](design/README.md) |

현재 순서: 확정 MVP 확인 → 조합 선택 → 최소 실행 → 구현 평가. 새 범위/후보의 비교에만 주제 선정 기준을 사용한다. 선정 기준은 평가 영역에, 실행 절차는 playbooks에 둔다.

작업 전 해당 폴더 AGENTS.md를 읽는다. CLAUDE.md는 같은 폴더 AGENTS.md를 @로 참조한다. 공식 source/revision과 내부 제안, 문서 확인과 실제 실행을 구분한다.
