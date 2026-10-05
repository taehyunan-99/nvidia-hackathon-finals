# 조사·대안 비교

[입출력 계약](../../catalog/contracts.md) · [합성 예시 JSON](../examples/research/fixtures.json) · [로컬 리허설](../rehearsal.md)

## 선택·준비

- 완료 산출물: 두 출처를 비교하고 근거 충돌을 드러내는 보고.
- 조합: Nemotron / NIM + NeMo Agent Toolkit + NeMo Retriever. 에이전트 형태는 `react`가 초기 후보이며 [선택표](../../catalog/agent-types.md)로 확인한다.
- 사용 입력·권한·필수 NVIDIA 조건을 [미션 카드](../templates/mission.md)에 먼저 적는다.

## 실행 순서

1. [최소 실행 안내](../quickstarts/nat.md)의 환경/입력 조건을 점검한다.
2. 아래 스킬 중 필요한 항목만 확보한다. 설치 명령은 최신 경로이므로 고정 버전이 필요하면 [확보 절차](../skill-setup.md)를 쓴다.
3. `허용 검색/MCP→출처 수집→추가 조사/종료→근거 보고`의 한 경로를 연결한다.
4. `출처/날짜/상충 내용 확인`로 결과를 확인한다.
5. 정보 부족/연결 실패 한 건을 넣어 보류/실패가 명확한지 확인하고 trace를 저장한다.

## 스킬과 사용 명령

- [nat-agent-configuration](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/SKILL.md) — `npx skills add NVIDIA/NeMo-Agent-Toolkit --skill nat-agent-configuration --agent codex --agent claude-code`
- [nat-mcp-and-serving](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-mcp-and-serving/SKILL.md) — `npx skills add NVIDIA/NeMo-Agent-Toolkit --skill nat-mcp-and-serving --agent codex --agent claude-code`

## 시간 제한·대안

핵심 경로 연결이 막히면 해당 도구 카드의 축소안으로 전환한다. 미실행 API를 성공으로 표시하지 않는다. 설치 시간·GPU 필요 여부는 [도구 카드](../../catalog/tools.md)의 해당 항목을 따른다.

## 구현 에이전트에 줄 요청

“조사·대안 비교 미션에서 두 출처를 비교하고 근거 충돌을 드러내는 보고를 만들자. Nemotron / NIM + NeMo Agent Toolkit + NeMo Retriever와 위 스킬의 필요성을 확인하고, 허용 검색/MCP→출처 수집→추가 조사/종료→근거 보고를 최소 입력 한 건으로 연결해줘. 성공 기준은 출처/날짜/상충 내용 확인이며 실패 입력도 함께 확인해줘.”

확인 상태: 설계/공식 사용법 조사. 미션용 서비스와 본선 API는 아직 실행하지 않았다.
