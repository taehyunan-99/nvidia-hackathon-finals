# 자원·일정 최적화

## 선택·준비

- 완료 산출물: 작은 작업 배분표와 목적값.
- 조합: Nemotron / NIM + NeMo Agent Toolkit + cuOpt. 에이전트 형태는 `tool-calling`가 초기 후보이며 [선택표](../../catalog/agent-types.md)로 확인한다.
- 사용 입력·권한·필수 NVIDIA 조건을 [미션 카드](../templates/mission.md)에 먼저 적는다.

## 실행 순서

1. [최소 실행 안내](../quickstarts/optimization.md)의 환경/입력 조건을 점검한다.
2. 아래 스킬 중 필요한 항목만 확보한다. 설치 명령은 최신 경로이므로 고정 버전이 필요하면 [확보 절차](../skill-setup.md)를 쓴다.
3. `목표→수학 모델→solver→검산→계획`의 한 경로를 연결한다.
4. `변수 범위·제약·목적값 독립 재계산`로 결과를 확인한다.
5. 정보 부족/연결 실패 한 건을 넣어 보류/실패가 명확한지 확인하고 trace를 저장한다.

## 스킬과 사용 명령

- [cuopt-numerical-optimization-formulation](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-numerical-optimization-formulation/SKILL.md) — `npx skills add NVIDIA/skills --skill cuopt-numerical-optimization-formulation --agent codex --agent claude-code`
- [cuopt-numerical-optimization-api](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-numerical-optimization-api/SKILL.md) — `npx skills add NVIDIA/skills --skill cuopt-numerical-optimization-api --agent codex --agent claude-code`

## 시간 제한·대안

핵심 경로 연결이 막히면 해당 도구 카드의 축소안으로 전환한다. 미실행 API를 성공으로 표시하지 않는다. 설치 시간·GPU 필요 여부는 [도구 카드](../../catalog/tools.md)의 해당 항목을 따른다.

## 구현 에이전트에 줄 요청

“자원·일정 최적화 미션에서 작은 작업 배분표와 목적값를 만들자. Nemotron / NIM + NeMo Agent Toolkit + cuOpt와 위 스킬의 필요성을 확인하고, 목표→수학 모델→solver→검산→계획를 최소 입력 한 건으로 연결해줘. 성공 기준은 변수 범위·제약·목적값 독립 재계산이며 실패 입력도 함께 확인해줘.”

확인 상태: 설계/공식 사용법 조사. 미션용 서비스와 본선 API는 아직 실행하지 않았다.
