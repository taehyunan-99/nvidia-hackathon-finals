# NVIDIA 구성요소 선택 가이드

2026-10-03 공식 문서/저장소 확인. 아래는 당일 선택을 위한 기술 후보이며 대회 필수 목록이 아니다. API 권한·설치·GPU·지연은 아직 본선 환경에서 검증하지 않았다.

## 역할부터 구분

**모델**은 추론/인식을 수행하고, **NIM**은 모델을 제공하는 추론 서비스, **NAT**는 도구를 연결·실행·관측·평가하는 틀이다. **Agent Skill**은 개발/운영 에이전트에게 주는 사용 지침이다. **Blueprint**는 참조 애플리케이션이며, **MCP**는 도구 연결 방식이다. 런타임에 스킬을 읽게 하더라도 실제 실행 함수를 별도로 제공하고 호출을 검증해야 한다.

## 공통 도구

| 구성 | 쓸 이유 / 입력→출력 | 최초 검증 | 조건·선택 경계 | 공식 자료 |
|---|---|---|---|---|
| Nemotron + Build/NIM | 목표·도구 schema→다음 도구/구조화 응답 | 텍스트 1회보다 실제 tool call→도구 결과→종료 1회를 확인 | 모델 ID·권한·쿼터별로 다름. hosted면 로컬 GPU 불필요, self-host는 모델별 GPU 조건 확인 | [Build](https://build.nvidia.com/explore/discover) · [NIM API](https://docs.api.nvidia.com/nim/) |
| NeMo Agent Toolkit (NAT) | 함수·모델·workflow→실행/trace/eval | 함수 1개 등록, 정상·실패 종료, trace 저장 | 기존 팀 경험을 우선할 후보. 공식 latest 문서 표기는 1.8, 예선 pyproject는 >=1.9,<2여서 버전 복사 전 실제 lock 확인 | [GitHub](https://github.com/NVIDIA/NeMo-Agent-Toolkit) · [문서](https://docs.nvidia.com/nemo/agent-toolkit/latest/index.html) |
| NeMo Retriever | 문서·표·이미지→추출/검색 근거 | 작은 문서 3개, 출처·페이지까지 연결 | 원격 서비스 client와 local GPU 경로를 구분. 스킬 현재 명시 버전은 26.8.1 | [GitHub](https://github.com/NVIDIA/NeMo-Retriever) |
| RAG Blueprint | 자료 corpus+질문→근거 기반 답 | 답 있는/없는 질문과 원문 대조 | 전체 stack이 무거우면 필요한 검색 경로만 선택. blueprint 설치 자체는 업무 완료가 아님 | [GitHub](https://github.com/NVIDIA-AI-Blueprints/rag) |
| NeMo Guardrails | 입력/출력/도구 정책→허용·거부 | 금지 요청과 정상 요청 한 쌍 | LLM 답변 정책 보조. JSON schema·업무 제약 검산을 대신하지 않음 | [문서](https://docs.nvidia.com/nemo/guardrails/about-nemo-guardrails-library/overview) |
| NeMo Data Designer | 데이터 정의→합성 사례 | 생성 5건 수동 검토·검증기 통과 | 미션이 정해진 뒤 경계 사례 확장. 생성 모델과 판정 모델만으로 정답을 확정하지 않음 | [GitHub](https://github.com/NVIDIA-NeMo/DataDesigner) |
| NAT 평가·관측 | 실행 기록+기대값→성공/실패·호출·지연 | 정상·실패 각 1건이 집계되는지 확인 | 품질과 latency를 분리. 시간 없으면 JSONL+결정적 검사로 시작 | [평가](https://docs.nvidia.com/nemo/agent-toolkit/latest/improve-workflows/evaluate.html) |
| NemoClaw | 지원 agent+실행 환경→관리되는 에이전트 runtime | 파일 1개 처리·허용/차단 범위 확인 | NAT의 대체 명칭이 아님. 특정 agent 운영이 미션에 맞을 때 | [GitHub](https://github.com/NVIDIA/NemoClaw) |
| OpenShell | 실행·네트워크 정책→격리된 실행 | 허용 파일/네트워크와 거부 동작 | 도구 실행 환경이 핵심일 때. 도입 비용을 기본 웹 앱에 강제하지 않음 | [GitHub](https://github.com/NVIDIA/OpenShell) |
| Brev | GPU 환경 구성→원격 개발/서빙 | 접속·nvidia-smi·컨테이너·작은 inference | 제공 자원과 비용 조건부터 확인. GPU가 있어도 모든 모델이 맞는 것은 아님 | [문서](https://docs.nvidia.com/brev/getting-started/overview) |

## 미션별 전문 도구

| 미션 | 후보 | 반드시 검증할 출력 | 선택 조건/공식 자료 |
|---|---|---|---|
| 배송·배차·자원 배분 | cuOpt | 제약 만족 여부, feasible 상태, 목적함수 | LLM이 제약을 만들고 solver가 계산, 독립 검산. local GPU/API 배치 조건 확인. [GitHub](https://github.com/NVIDIA/cuopt) |
| 영상 검색·안전 이벤트 | VSS, 필요 시 DeepStream | 답과 실제 시간 구간·프레임의 일치 | 전체 영상 인프라가 이미 있거나 핵심 미션일 때. 없으면 짧은 clip 최소 경로부터. [VSS](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization) |
| 음성 업무 | Nemotron Speech/Riva | 전사·발화/텍스트 대안·업무 완료 | 마이크/언어/오디오 포맷·streaming 확인. [공식 스킬](https://github.com/NVIDIA/skills/tree/main/skills/nemotron-speech) |
| 생명과학 | BioNeMo NIM, Boltz-2/DiffDock/GenMol | 구조·분자 형식·대응 검증과 모델별 한계 | 전문 미션일 때만. 구조 신뢰도는 실험적 효능이 아님. [Build Biology](https://build.nvidia.com/explore/discover) · [스킬](https://github.com/NVIDIA/skills/tree/main/skills/bionemo-boltz2-nim) |
| 추론 서빙 성능 | Dynamo | 같은 입력의 처리량·지연·자원 사용 | 다중 요청/서빙이 병목일 때만. 단일 데모 전에 도입하지 않음. [공식 스킬](https://github.com/NVIDIA/skills/tree/main/skills/dynamo-recipe-runner) |

제품명을 많이 붙이는 것보다 **문제→선택 이유→실제 호출→검증된 결과**가 한 줄로 이어지는 구성을 택한다. 각 스킬의 정확한 주소는 [전체 인덱스](skills-index.json), 적용 조합은 [선택표](../playbooks/recipes.md)에 있다.

## 개별 실행 카드

- [Nemotron / NIM](tools/nim.md) — 목표와 관측에서 다음 행동을 선택하는 모델·추론 endpoint
- [NeMo Agent Toolkit](tools/nat.md) — 모델·함수·MCP를 workflow로 연결하고 실행/관측
- [NeMo Retriever](tools/retriever.md) — 문서·표·이미지를 추출하고 출처가 있는 검색 결과 생성
- [RAG Blueprint](tools/rag.md) — 검색·생성·검증을 묶은 참조 애플리케이션
- [NeMo Guardrails](tools/guardrails.md) — 입력·출력·대화 정책을 검사
- [NeMo Data Designer](tools/data-designer.md) — schema·생성 규칙으로 합성 평가 데이터 작성
- [NAT evaluation / telemetry](tools/evaluation.md) — 고정 입력으로 작업 성공·도구 경로·지연 비교
- [NemoClaw](tools/nemoclaw.md) — 선택한 agent를 관리된 inference·격리 환경에서 운영
- [OpenShell](tools/openshell.md) — agent 실행의 파일/네트워크/프로세스 경계를 관리
- [Brev](tools/brev.md) — GPU 환경을 마련해 원격 개발·컨테이너 실행
- [cuOpt](tools/cuopt.md) — 배차·경로 또는 LP/MILP/QP 제약 최적화
- [Video Search and Summarization](tools/vss.md) — 영상 검색·시각 질의·시간 구간 요약
- [Nemotron Speech / Riva](tools/speech.md) — 음성 인식·합성·번역을 업무 도구와 연결
- [BioNeMo NIM](tools/bionemo.md) — 구조/분자 생성·예측 전문 도구
- [DeepStream](tools/deepstream.md) — 실시간 영상의 decode·추론·추적 pipeline
- [Dynamo](tools/dynamo.md) — 여러 inference 요청의 서빙/라우팅 성능 조정
- [RAPIDS / cuDF](tools/rapids.md) — 대규모 표 데이터 처리 가속
- [Physical AI / Isaac / Cosmos](tools/physical-ai.md) — 물리 환경·로봇·영상 생성/시뮬레이션 미션 탐색
