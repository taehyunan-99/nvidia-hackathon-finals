# 에이전트·실행 형태 선택

에이전트는 역할/판단 흐름, 모델은 추론기, NAT는 연결/실행 틀이다. NemoClaw/OpenShell은 운영 runtime이며 이 표의 agent 타입과 같은 층이 아니다.

| 형태 | NAT `_type` | 선택할 상황 | 준비·성공 확인 |
|---|---|---|---|
| Tool Calling | `tool_calling_agent` | 명확한 schema 도구에서 다음 행동을 선택 | native tool calling 모델·함수 등록; 모델이 실제 도구 인자를 생성하고 반환 결과를 사용해 종료; structured output도 별도 schema 검사 |
| ReAct | `react_agent` | 관측→다음 호출을 반복하며 조사 | 선택 모델의 텍스트/네이티브 모드 지원; Action 파싱/도구 선택/종료 확인; 모델이 도구 호출 없이 답만 만들면 통과 아님 |
| Router | `router_agent` | 요청을 하나의 전문 분기로 분류 | 분기 목록과 경계/모호 입력 정책; 서로 다른 두 입력이 적절한 분기로 가는지; 여러 분기 실행용이 아님 |
| Sequential Executor | `sequential_executor` | 고정 순서 변환·검산 | 각 단계 입력/출력 호환; 중간 실패가 뒤 단계에 성공값으로 전달되지 않음; executor 자체는 LLM 판단 없음 |
| Parallel Executor | `parallel_executor` | 독립 조회/분석을 동시에 실행 | 독립 도구·공유 호출 예산; 부분 실패·순서 비의존·한도 준수; 앞 단계 출력이 필요하면 순차 실행 |
| Reasoning | `reasoning_agent` | 먼저 계획하고 내부 agent에 위임 | thinking 지원 모델·내부 함수; 추가 계획 비용 대비 결과 이득을 기준선으로 검증 |
| ReWOO | `rewoo_agent` | 계획/도구 실행/결과 합성을 분리 | 사전 분해 가능한 작업과 도구 입력; 계획의 의존성·중간 실패 확인; 관측마다 계획 변경이 핵심이면 다른 패턴 검토 |
| Responses API Agent | `responses_api_agent` | Responses 호환 모델의 내장/MCP 도구 연결 | 해당 endpoint가 Responses API 지원; chat-completions 호환만으로 가정 금지; 서버 도구 호출·응답 지원을 확인 |
| Auto Memory Wrapper | `auto_memory_agent` | 여러 턴/세션에 이전 정보를 유지 | memory backend·저장 범위·세션 분리; 새 세션 간 데이터 혼합 없는지·삭제 정책·history가 결과를 바꾸는지 확인 |

## 1분 결정

실행 순서가 고정이면 sequential, 독립 작업을 모두 실행하면 parallel, 한 갈래만 고르면 router를 검토한다. 도구 결과를 보고 다음 행동을 고르면 tool-calling/ReAct가 후보이다. 계획·장기 memory는 필요한 이득과 설치 시간이 확인될 때만 추가한다.

기본 후보는 native tool calling을 지원하는 모델+단일 agent+소수의 도구다. 실제 모델/endpoint 지원을 먼저 확인한다. 여러 agent로 나눴다는 사실 자체를 자율성이나 품질 향상으로 채점하지 않는다.

## 설정·실행

공통 시작은 [NAT 최소 실행](../playbooks/quickstarts/nat.md). 에이전트별 설정은 [고정 버전 공식 참고](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/references/agents.md)와 [추가 타입](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/references/additional-agent-types.md)을 해당 타입만 읽는다. 설치 버전의 `nat info components`와 schema가 우선한다.

9개 유형은 문서상의 목록이며 본선 환경에서 9개 모두 실행했다는 뜻이 아니다. [공식 문서](https://docs.nvidia.com/nemo/agent-toolkit/latest/components/agents/index.html).
