# 가족 문화체험 에이전트 설계 진입

기존 제안 설계는 [ARCHITECTURE](../ARCHITECTURE.md)로 이관했다. 모델·프레임워크·배치의 채택 상태는 [ADR](../ADR.md), 요구사항과 수용 기준은 [PRD](../PRD.md)를 따른다. 최종 필드 schema와 실제 연결은 여전히 미확정·미검증이다.

## 최소 흐름과 책임

[논리 구성과 책임](../ARCHITECTURE.md#논리-구성과-책임)을 참조한다.

## 도구와 상태 계약 — 제안

[데이터 계약](../ARCHITECTURE.md#데이터-흐름과-계약-초안)과 [상태·복구](../ARCHITECTURE.md#상태와-복구-초안)를 참조한다.

## 판단이 바뀌어야 하는 대표 상황

[검증 시나리오](../PRD.md#검증-시나리오)를 참조한다.

## OpenShell과 공통 테스트

[실행·보안 경계](../ARCHITECTURE.md#실행보안-경계)와 [공식 미션](../operations/mission.md)을 참조한다.

에이전트 구현 전 최소 보안 기반은 [OpenShell 하네스](../playbooks/openshell-harness.md)에 구현돼 있다. 다음 작업은 실제 챌린지 패키지를 보존해 배치하고, 팀원 에이전트·자료 도구·결과 회수를 연결한 뒤, 동일한 최종 정책에서 정상 과업·추가 조건·금지 접근·반출을 재검증하는 것이다. 합성 검사 통과를 실제 챌린지 완주로 표시하지 않는다.

## 스킬·확장·검증

에이전트·자료 도구·개발 스킬은 [구현 기준 조합](../ARCHITECTURE.md#구현-기준-조합)을 따른다. 단일 NAT ReAct를 사용하며 `nat-agent-configuration`, `nat-tools-and-functions`를 개발 지침으로 선택했다. 스킬 설치만으로 런타임 함수가 생기지 않는다. [공통 흐름](../playbooks/agent-flow.md)·[하네스](../playbooks/harness.md)·[공통 계약](../catalog/contracts.md)은 재사용 자료이며 제품 구현 성공이나 최종 schema가 아니다.

화면에는 `nvidia-ui`를 재사용하고, `agent-rubric`·`frontend-rubric`·`submission-check`는 각각 실제 판단·화면·필수 경계를 확인한다. [주제 선정 기준](../evaluation/topic-selection.md)과 구현 품질·공식 배점은 구분한다. 검사 선택은 [CI 원칙](../operations/ci-policy.md)을 따른다.
