# 다른 조합의 입출력과 프런트 계약

조사 조합은 [research-v1](../contracts.md), 나머지 기존 미션 조합 9개는 이 문서를 사용한다. 목적은 조합을 고르면 프런트가 입력 폼·진행 상태·결과 영역을 바로 가정할 수 있게 하는 것이다. 공식 형식 조사일은 2026-10-05이며 아래 공급자 호출은 이번 작업에서 실행하지 않았다.

## 바로 사용하는 파일

- [mission-v1 JSON Schema](mission.schema.json): `recipe`에 따라 입력과 출력 타입을 선택한다. NVIDIA 표준 API가 아닌 프로젝트의 프런트 계약이다.
- [9개 조합 × 정상·보류·실패 JSON](mission-fixtures.json): `fixtures[recipe][completed|partial|failed]`로 접근한다. 모든 값은 합성이며 `fixture://`는 실파일 주소가 아니다.
- `python3 scripts/lookup.py --show recipe:routing`처럼 조합을 찾으면 contract·contract_section·schema·fixtures를 함께 받는다.

공급자의 반환 객체/문자열/파일을 서버 adapter에서 `mission-v1`으로 변환한다. 공급자 필드를 그대로 프런트에 요구하지 않는다. 아래의 **정규화 입력/출력**은 합의 가능한 프로젝트 설계이며 실제 모델·서비스 버전의 요청 JSON과 동일하다는 뜻이 아니다. 검색 텍스트, 이진 오디오, mmCIF, DataFrame은 같은 타입으로 취급하지 않는다.

## 공통 연결

| 필드 | 타입·사용법 |
|---|---|
| `schema_version`, `recipe`, `run_id`, `input_hash` | `mission-v1`, 조합 식별자, 실행 ID, 입력의 SHA-256; 이전 실행과 혼합하지 않음 |
| `mode`, `model_id`, `http_requests` | mock/replay/live·모델 식별자·실제 요청 수; mock은 null·0 |
| `input`, `output` | 아래 조합별 타입; 미수신 output은 null, 보류의 확인된 부분 결과는 output에 보존 |
| `events` | 기존 seq/kind/label/status/reason/tool/attempt/error_code/evidence_ids; tool은 조합별 문자열 |
| `evidence` | `{id:string, source:string, quote:string}[]`; 상세 페이지·구간·좌표 등은 조합별 output에 포함 |
| `artifact` | 완료에서만 `{summary:string, evidence_ids:string[]}`; 보류·실패·취소는 null |
| `limitations`, `next_action` | 미검증 범위와 재입력·자료 확보·연결 점검 안내 |

`completed`는 형식 검사 외에 조합별 완료 조건까지 통과한 상태다. 도구가 응답했거나 작업 ID를 반환했다고 완료로 바꾸지 않는다. 정상 예시는 검증 통과를 **가정한 합성값**이며 provider 연결 검증이 아니다. 비동기 submit/poll은 서버에서 공급자 job ID를 run ID에 연결하고, 아직 끝나지 않았으면 running을 유지한다. 기존 모델 호출 예산과 실제 요청 집계·재시도를 재사용한다.

오류는 공통 invalid_input/unavailable/timeout/rate_limited/invalid_output 외에 permission_denied와 infeasible을 사용한다. 불가능한 제약은 partial, 전송·실행 실패는 failed이며 실제 HTTP/gRPC/CLI 오류 매핑은 adapter에서 확인한다. 취소는 cancelled로 구분하고 이 예시는 취소 실행을 구현하지 않는다.

화면 스타일과 사건 순서 표시는 기존 [실행 흐름 컴포넌트](../../design/agent-flow.md)를 재사용한다. **현재 화면은 research-v1 전용**이며 mission-v1 예시를 바로 로드하는 화면은 만들지 않았다. 새 조합에서는 tool 표시 이름을 추가하고 `output`의 표·구간·파일 등 결과 렌더러를 붙인다. 파일 ref는 서버가 접근을 확인한 다운로드 경로로 바꾸고, 인증 헤더·바이너리·모델 내부 추론은 이벤트에 넣지 않는다.

<a id="documents"></a>
## 문서·규정 검토

조합: NIM 판단 + NAT 검색 함수 + NeMo Retriever. 스킬: `nat-tools-and-functions`, `nemo-retriever`.

- 정규화 입력: `question:string`, `documents:{ref,media_type}[]`, `items:string[]`.
- 도구 입출력: 문서를 ingest한 뒤 query/top-k로 검색 → 텍스트와 원문 출처·페이지 metadata. [고정 Retriever 스킬](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-retriever/SKILL.md)은 CLI `--format evidence`와 출처 보존을 안내한다. 서비스/추출 모델의 실제 응답 키는 해당 버전에서 확인한다.
- 정규화 출력: `items:{item,verdict,quote,document_ref,page}[]`; verdict는 supported/unsupported/unknown/conflict, page는 1부터 시작하거나 null.
- 프런트: 질문·문서 목록·검토 항목 입력 → 항목별 판정/인용/페이지 표. 자료 없음은 unknown과 null 위치이며 인용을 생성하지 않는다.
- 완료 검사: 인용이 지정 원문의 실제 위치와 일치하고 각 항목의 판정이 근거로 검증됨. 단순 검색 점수는 충족 판정이 아니다. 미지원 주장·없는 페이지는 거부한다.

<a id="routing"></a>
## 배송·배차·경로

조합: NIM 제약 해석 + NAT solver 함수 + cuOpt routing. 스킬: `cuopt-routing-api-python`.

- 정규화 입력: 정사각 `cost_matrix:number[][]`, `time_unit:"minute"`, `vehicles:{id,capacity,depot}[]`, `orders:{id,location,demand,time_window:[start,end]}[]`. 이 작은 계약의 비용은 이동 분이며 서비스 시간은 0이다. 다른 비용·서비스 시간을 추가하면 계약도 확장한다.
- 도구 입출력: Python `DataModel`에 비용행렬·주문 위치·시간창·용량을 설정 → `Solve`의 solution 객체. `get_status()`, `get_route()`, `get_total_objective()`를 서버에서 읽어 아래로 변환한다. [고정 routing API 스킬](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-routing-api-python/SKILL.md). REST submit/poll 규격을 Python 객체와 섞지 않는다.
- 정규화 출력: `solver_status`, `routes:{vehicle_id,order_ids,locations,arrival_minutes,load}[]`, `objective:number|null`, `unserved_order_ids:string[]`. raw 숫자 상태를 feasible/infeasible/timeout으로 매핑하되 feasible을 최적해로 표현하지 않는다.
- 프런트: 비용행렬·방문지·차량 폼 → 차량별 방문 순서/시각/부하와 미방문 목록.
- 완료 검사: 행렬 크기·인덱스·단위, 전 주문 1회 방문, 출발/귀환 depot, 용량·시간창·총 비용을 원본으로 재계산. 불가능하면 제약을 삭제하지 않고 partial로 표시한다.

<a id="allocation"></a>
## 자원·일정 최적화

조합: NIM 수학 모델 해석 + NAT solver 함수 + cuOpt LP/MILP. 스킬: `cuopt-numerical-optimization-formulation`, `cuopt-numerical-optimization-api`.

- 정규화 입력: `sense:minimize|maximize`, `variables:{id,lower,upper,integer}[]`, `objective:number[]`, `constraints:{coefficients:number[],sense:le|eq|ge,rhs:number}[]`. 계수 순서는 variables 순서와 같다. 시간 일정은 같은 변수/제약으로 표현하며 이 계약에 범용 달력 기능은 없다.
- 도구 입출력: Python Problem의 변수·제약·목적식 → solve → Status/ObjValue와 변수 Value. [공식 LP/MILP API](https://docs.nvidia.com/cuopt/user-guide/latest/cuopt-python/lp-milp/lp-milp-api.html)에서 확인한 객체 경로이며 실제 설치 버전의 API가 우선한다.
- 정규화 출력: `solver_status:optimal|feasible|infeasible|unbounded|timeout`, `values:{variable_id,value}[]`, `objective:number|null`, `checks:{name,passed}[]`.
- 프런트: 변수·계수·제약 표 → 값/목적값/제약 검산 표. 해가 없는 상태에서는 확정 배분표를 숨긴다.
- 완료 검사: 벡터 길이·변수 경계·정수성·모든 제약·목적값 독립 재계산. feasible은 optimal과 별도 표시하며 허용 오차는 실제 미션 단위에 맞춰 정한다.

<a id="operations"></a>
## 장애·업무 처리

조합: NIM 판단 + NAT typed 조회/조치/재조회 함수. 스킬: `nat-tools-and-functions`, `nat-telemetry`.

- 정규화 입력: `resource_id:string`, `allowed_actions:string[]`, `idempotency_key:string`. 예시는 inspect만 허용하며 외부 변경을 수행하지 않는다.
- 도구 입출력: 서버가 정의한 상태 조회·권한 있는 조치 인자 → typed 상태·조치 결과 → 재조회. NAT는 특정 티켓·운영 API를 정의하지 않는다. [고정 NAT 함수 문서](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-tools-and-functions/references/tools-and-functions.md).
- 정규화 출력: `before:string`, `action:string|null`, `after:string|null`, `verified:boolean`.
- 프런트: 리소스·허용 조치 입력 → 전/후 상태와 검증. 미허용 조치는 선택지에서 제거하고 권한 부족을 partial로 표시한다.
- 완료 검사: 도구 권한·동일 작업의 중복 실행 차단·재조회 상태로 목표 달성 확인. 조치 접수만으로 성공하지 않는다. 실제 제품 API 인자·오류는 미션이 정한 시스템의 schema로 adapter에 연결한다.

<a id="video"></a>
## 영상 검색·검토

조합: NIM/VSS agent + 기존 영상 검색 또는 video_understanding. 스킬: `vss-ask-video`, `vss-search-archive`.

- 정규화 입력: `question:string`, `video:{ref,media_type}`, `duration_seconds:number`.
- 도구 입출력: 고정 VSS profile의 `/generate`는 `{input_message:string}` → `{value:string}`. [고정 vss-ask-video 스킬](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-ask-video/SKILL.md). value의 agent-think 부분을 제거하고 답만 사용한다. raw value에 프레임·시간 구조가 보장된다고 가정하지 않는다.
- 정규화 출력: `answer:string|null`, `segments:{start_seconds,end_seconds,frame:{ref,media_type},observation}[]`, `visually_verified:boolean`. 구간·프레임은 선택 profile의 실제 근거에서 확보하고 없는 값을 만들지 않는다.
- 프런트: 영상·질문 입력 → 답/구간 목록/프레임. 시간은 클립 시작 기준 초이며 벽시계 시각과 구분한다.
- 완료 검사: 0 ≤ start < end ≤ duration, 원본 프레임 대조, 질문과 사건 일치. 메타데이터만 확보했거나 시각 근거가 없으면 partial이며 확정 사건을 표시하지 않는다.

<a id="voice"></a>
## 음성 업무

조합: Speech ASR + NIM 판단 + NAT 업무 함수; 필요할 때만 TTS. 스킬: `nemotron-speech`, `nemotron-voice-agent-builder`.

- 정규화 입력: `audio:{ref,media_type}`, `encoding:string`, `sample_rate_hz:integer`, `language_code:string`, `task:string`. 형식·sample rate·언어 지원은 선택 모델에서 확인한다.
- 도구 입출력: Riva gRPC RecognizeRequest의 config(encoding/sample_rate_hertz/language_code)+audio bytes → RecognizeResponse의 results[].alternatives[].transcript. streaming은 별도 RPC이며 is_final이 참인 구간을 확정한다. [공식 proto 고정 commit](https://github.com/nvidia-riva/common/blob/268890b7286031a6d4950e34f7ce13ed0d4ce621/riva/proto/riva_asr.proto). word 시간은 제공될 때 밀리초이므로 UI 초로 변환한다.
- 정규화 출력: `transcript:string`, `final:boolean`, `task_result:string|null`, `audio_reply:{ref,media_type}|null`. ASR 전사와 업무 결과를 구분하고 TTS 바이트는 파일 ref로 전달한다.
- 프런트: 오디오 입력 → 전사 확정 상태 → 업무 결과·선택적 음성 재생. 무음/불명확 발화는 재입력 또는 텍스트 입력 안내.
- 완료 검사: 알려진 문장 대조·최종 전사 여부·업무 도구 반환 결과. 전사 성공만으로 업무 완료하지 않는다. 언어·마이크·TTS 호출은 이번에 실행하지 않았다.

<a id="biology"></a>
## 분자·구조 검토

조합: NIM 판단 + NAT 근거 조회/검증 + Boltz-2. 스킬: `bionemo-boltz2-nim`(선언 이름 boltz2-nim).

- 정규화 입력: `polymers:{id,molecule_type:protein|dna|rna,sequence}[]`, `existing_structures:{ref,media_type}[]`.
- 도구 입출력: Boltz-2 predict의 polymers·선택적 ligands/constraints → structures[].structure(mmCIF 문자열), confidence_scores[], 선택적 affinities. [고정 API 문서](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/bionemo-boltz2-nim/references/api.md). 서버는 mmCIF를 보관하고 파일 ref로 변환한다. 여기에 DiffDock/GenMol 형식을 섞지 않는다.
- 정규화 출력: `structures:{file,chain_ids,sequence_match,coordinate_check,confidence:number|null,provenance:experimental|predicted}[]`, `interpretation:string`.
- 프런트: 사슬·서열·기존 구조 입력 → 출처/검증/신뢰도 표·파일 다운로드. 3D는 미션에서 필요할 때 추가한다.
- 완료 검사: 요청 사슬·서열·좌표와 결과 대응, 실험/예측 구분. 모델 신뢰도와 ligand affinity를 항체 결합력·효능 증명으로 바꾸지 않는다. 예측 API·파일 파싱은 이번에 실행하지 않았다.

<a id="data"></a>
## 표 데이터 분석

조합: NIM 계산 선택 + NAT 함수 + cuDF. 스킬: `accelerated-computing-cudf`.

- 정규화 입력: `dataset:{ref,media_type}`, `columns:{name,dtype}[]`, `group_by:string[]`, `value_column:string`, `aggregation:sum|mean|count`.
- 도구 입출력: read_csv/read_parquet → DataFrame 연산 → DataFrame. [고정 cuDF 스킬](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/accelerated-computing-cudf/SKILL.md)은 최종 경계에서 CPU/표시 타입으로 변환하고 nullable·정렬·수치 허용 오차를 보존하도록 안내한다. GPU 객체는 JSON 응답이 아니다.
- 정규화 출력: `columns:string[]`, `rows:(string|number|boolean|null)[][]`, `row_count:integer`, `cpu_parity:pass|fail|unverified`, `duration_ms:number`.
- 프런트: 데이터·열·집계 선택 → 결과 표와 검산/시간. 날짜·Decimal 등은 adapter의 명시 규칙으로 변환하며 NaN은 JSON null로 처리한다.
- 완료 검사: 열·행 수·null 위치·정렬과 CPU 계산 대조. 확인되지 않은 결과는 partial output으로 보여주고 확정 artifact를 만들지 않는다. 합성 duration은 GPU 가속 실측이 아니다.

<a id="sandbox"></a>
## 격리된 에이전트 운영

조합: NemoClaw의 선택 agent + OpenShell 정책·실행 관측. 스킬: `nemoclaw-user-guide`.

- 정규화 입력: `goal:string`, `allowed_read:string[]`, `allowed_write:string[]`, `allowed_hosts:string[]`, `output_ref:string`.
- 도구 입출력: OpenShell 정책은 YAML의 version/filesystem_policy/process/network_policies 등으로 접근을 관리하고, 선택 runtime의 실행 결과·로그·산출물을 관측한다. [공식 정책 설명](https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview). NemoClaw variant별 명령은 [공식 문서](https://docs.nvidia.com/nemoclaw/llms.txt)에서 선택한다. runtime에 공통 JSON task endpoint가 있다고 가정하지 않는다.
- 정규화 출력: `files:{ref,media_type}[]`, `denied_accesses:string[]`, `scope_verified:boolean`, `exit_code:integer|null`.
- 프런트: 목표·허용 범위 입력 → 결과 파일/차단 항목/실행 상태. 정책 적용과 산출물 완료를 별도로 표시한다.
- 완료 검사: 허용 위치의 산출물 내용·요청 대응, 금지 파일/endpoint 차단, 종료 상태. 접근 거부는 정상적인 경계 관측일 수 있으며 그 자체가 작업 성공은 아니다. 정책·runtime 설치는 실행하지 않았다.

## 에이전트와 개발 스킬의 입출력 경계

위 조합의 agent에는 목표·정규화 입력·현재 관측·허용 도구·완료 조건을 제공한다. agent의 도구 선택 응답은 공급자 형식이며 adapter가 검사하고, 프런트에는 검증된 이벤트·조합별 output·artifact만 전달한다.

| 에이전트 형태 | 입력 → 내부 출력·연결 | 프런트에 전달할 것 |
|---|---|---|
| Tool Calling / ReAct | 목표·도구 schema·관측 → native call 또는 텍스트 action → 도구 반환 → 다음 판단 | 도구/선택 이유/검증/최종 결과; ReAct 원문 추론은 제외 |
| Router | 입력·분기 목록 → 선택한 단일 분기의 응답 | 선택된 조합과 해당 조합 계약; 다른 분기를 실행한 것처럼 표시하지 않음 |
| Sequential / Parallel Executor | 함수 입력 → 이전 출력/독립 출력들 → 합성 | 단계별 상태와 부분 실패; executor 자체를 모델 판단으로 표시하지 않음 |
| Reasoning / ReWOO | 목표·내부 함수·의존 관계 → 계획·호출·합성 | 검증된 실행 기록과 결과; 미실행 계획은 실행 이벤트가 아님 |
| Responses API Agent | 지원 endpoint의 요청·도구 → provider response items | adapter 변환 후 동일 계약; chat endpoint 지원에서 Responses 지원을 추정하지 않음 |
| Auto Memory Wrapper | 세션 ID·history·내부 agent 입력 → 내부 결과·memory 변경 | 현재 실행 결과; 다른 세션 기억을 출력하지 않음 |

[NAT 고정 agent 문서](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/references/agents.md)와 [추가 형태](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/references/additional-agent-types.md)를 따른다. 모든 agent가 동일 structured response를 직접 반환한다는 가정은 하지 않는다.

개발 스킬은 runtime 도구가 아니다. 각 조합에 적힌 스킬에는 **목표·입력 예시·해당 도구 버전·환경·허용 범위·이 문서의 입출력·완료 검사**를 제공하고, **설정/함수/adapter 코드와 확인 절차**를 받는다. 예를 들어 cuOpt 스킬은 제약 모델·solver 호출 코드를 만들며 경로 JSON을 실제 계산 없이 반환하는 API가 아니다. nvidia-ui에는 조합별 fixture·필요한 입력/결과 영역을 주고 화면 코드를, agent-rubric에는 구현·현재 실행 근거를 주고 점수·미확인·개선 의견을 받는다. 선택한 스킬의 상세 입력은 원문 조건을 우선한다.
