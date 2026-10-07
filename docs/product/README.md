# 가족 문화체험 제품 문서

목적·범위·요구사항·구조·결정 이유는 아래 문서에서 각각 관리한다. 문서의 확정 범위와 제안·미결정을 구분하며 구현·실행 성공으로 해석하지 않는다.

| 문서 | 원본 역할 |
|---|---|
| [INTENT](../intent/INTENT.md) | 사용자 문제·목적·가치·기능 방향과 경계 |
| [PRD](../PRD.md) | 사용자 흐름·요구사항·완료/보류·수용 기준·인터뷰 미결정 |
| [ARCHITECTURE](../ARCHITECTURE.md) | 구성요소 책임·데이터 흐름·실행/보안 경계·구현 미결정 |
| [ADR](../ADR.md) | 결정의 배경·대안·이유·영향과 채택 상태 |
| [데이터와 근거](data-sources.md) | 실제 출처·조회 범위·자료 접근과 확장 한계 |
| [family-v1 계약](../catalog/contracts/family-v1.md) | 가족 검증 입력·출력·도구·질문 재개와 합성 시험의 기대 판정; 구현 성공은 아님 |

기존 MVP·선택 기능·성공 기준은 INTENT와 PRD로, 제안 계약은 ARCHITECTURE로 이관했다. 선택 기능의 데이터·제약은 데이터와 근거 문서에서 확인한다. [에이전트 설계 진입](agent-design.md)은 새 설계와 기존 실행 자료를 연결한다.

## 관련 운영 자료

- [공식 미션](../operations/mission.md): 필수 조건·공통 테스트·제출 요건의 원본.
- [운영 기준](../operations/workflow.md): 2인 분담·일정·배포 방향; 개인별 담당 미확정.
- [AWS–Brev 연결](../playbooks/aws-brev-deployment.md): 배치·인증·복구의 조사와 기존 모델 없는 연결 시험; 실제 에이전트 통합과 구분.
- [프런트 구현](../../frontend/README.md) · [Docker·AWS 수동 배포](../playbooks/frontend-deployment.md): 공개된 합성 예시 화면의 실행·검증·운영 경계.
- [OpenShell 하네스](../playbooks/openshell-harness.md): 합성 파일·반출·결과 회수 검증과 실제 패키지 배치→에이전트 연결→최종 정책 재검증의 남은 세 조치.

개인 인계 파일과 `docs/plan.md`는 위 제품 문서를 대체하지 않는다.
