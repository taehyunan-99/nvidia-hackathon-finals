# 새 미션을 받았을 때의 조합 선택표

[주제 선정 기준](../evaluation/topic-selection.md)으로 비교한 후보에 적용하는 조합 안내다. 아래 구성은 공식 강제 조건이 아닌 7시간 개발용 제안이다. 새 미션의 사용자·입력·정답/성공 조건을 먼저 [양식](templates/mission.md)에 적는다.

## 조합 선택 순서

1. 사용자가 끝내려는 일과 현재 실패 상태를 한 문장씩 쓴다. 산출물이 답변/계획/파일/실행 중 무엇인지 정한다.
2. 결과를 틀렸다고 판정할 검증법과 실제 입력 1개를 확보한다. 검증할 수 없다면 범위를 줄인다.
3. 모델이 판단할 분기 한 곳을 정하고, 계산·권한·완료 판정은 도구/코드에 둔다.
4. 해당 조합의 최소 경로를 최소 입력으로 연결한다. 연결되지 않으면 아래 축소 경로로 전환한다.

## 구성별 최소 조합

| 유형·관찰 가능한 완료 | 에이전트·실행 도구 | 개발 스킬 폴더 | 첫 검증/축소 경로 |
|---|---|---|---|
| 문서에서 규정 위반 확인 → 인용 있는 검토표 | Nemotron+NAT, Retriever, 필요 시 RAG Blueprint | nat-workflow-creation, nat-tools-and-functions, nemo-retriever; 전체 blueprint면 rag-blueprint/rag-eval | 원문 3개와 정상/위반/자료 없음 사례. 전체 vector DB보다 작은 corpus부터 |
| 조사·대안 비교 → 출처와 근거 충돌이 있는 보고 | Nemotron+NAT, 허용된 검색/MCP, 결정적 근거 검사 | nat-agent-configuration, nat-mcp-and-serving, nat-evaluation | 출처 누락 시 추가 수집 또는 보류. 검색 장애는 답 없음과 구분 |
| 배차·일정·자원 배분 → 제약을 만족하는 계획 | Nemotron+NAT, cuOpt, 제약 재검산 함수 | cuopt-numerical-optimization-formulation; LP/MIP면 cuopt-numerical-optimization-api, 경로면 cuopt-routing-api-python | 작은 5개 작업으로 feasible/infeasible. solver 미연결 시 규칙 baseline을 명시하고 NVIDIA 핵심 요구 재확인 |
| 장애/업무 티켓 → 진단·조치안·검증 | Nemotron+NAT, 상태 조회/API, 조치 검증 함수 | nat-tools-and-functions, nat-telemetry; 격리가 중요하면 nemoclaw-user-guide | 읽기→계획→sandbox 변경→재확인. 외부 변경 권한이 없으면 검토 가능한 조치안까지 |
| 영상 이벤트 → 해당 구간과 확인 근거 | Nemotron/VLM+VSS, 필요 시 NAT | vss-deploy-profile, vss-search-archive, vss-ask-video | 20초 clip과 사람이 확인한 시각. 전체 VSS가 늦으면 짧은 clip tool로 범위 축소 |
| 음성 요청 → 전사와 실제 업무 결과 | Nemotron Speech+Nemotron+NAT | nemotron-speech, nemotron-voice-agent-builder | 3개 발화, 잡음/미지원 입력. 텍스트 대안 유지 |
| 분자/구조 검토 → 검증 가능한 구조 근거 | Nemotron+NAT+해당 BioNeMo NIM+구조 validator | bionemo-boltz2-nim 또는 bionemo-diffdock-nim | 공개 기준 구조 1개와 입력 불일치 1개. 검증 불가능한 효능/순위는 산출물에서 제외 |

스킬명은 [정확한 경로와 선언 이름](../catalog/skills-index.json)으로 조회한다. 경로 이름과 설치 선택 이름이 다를 수 있다.

## 기본 에이전트 형태

- 단일 tool-calling agent + 2~4개 도구 + 검증기부터 시작한다. 스스로 다음 호출을 고르는 분기를 trace로 입증한다.
- 작업이 고정 순서라면 sequential workflow가 더 단순하다. 고정 pipeline을 자율 판단으로 포장하지 않는다.
- 서로 다른 정보원/역할을 분리하면 실제 이득이 있고 시간 내 통합 가능한 경우에만 router 또는 다중 에이전트를 추가한다.
- 학습·대형 모델 교체는 기본 준비 항목이 아니다. 모델이 충분하면 데이터·도구 계약·검증·지연을 먼저 개선한다.

## 선택 기록

<!-- prev: 예상효용·자료 접근·초기 연결·검증의 4항목 선별표 → 2026-10-05 사용자 승인으로 주제 선정 기준에 통일. -->
후보의 점수·관문·미확인 처리는 [주제 선정 기준](../evaluation/topic-selection.md)을 단일 원본으로 사용한다. 이 문서는 선택한 주제의 도구 조합과 축소 경로만 정하며 별도 선별 점수를 만들지 않는다. 선택한 범위와 검증 방법은 [미션 카드](templates/mission.md)에 기록한다.
