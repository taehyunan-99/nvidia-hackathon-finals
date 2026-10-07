# 입출력 계약과 프런트 연결

대표 조합: **조사·대안 비교 → NIM 판단 + NAT 도구 연결 + 근거 조회 도구**. 이번에 실행 가능한 것은 아래 프로젝트 계약의 오프라인 리허설이다. NIM의 실제 도구 선택과 새 합성 입력 두 개의 관측 기반 실행 제어를 확인했으며, NAT·Retriever 연결은 실행하지 않았다. 기존 다른 미션 조합 9개의 도구 반환 형태·프런트 계약·스킬 경계는 [다른 조합의 입출력](contracts/combinations.md)에 정리했다. 전체 제품·스킬의 모든 API를 조사 완료한 목록은 아니다.

| 바로 할 일 | 파일 |
|---|---|
| 가족 검증기·에이전트 병행 개발 | [family-v1 계약·판정 규칙](contracts/family-v1.md) · [schema](contracts/family-v1.schema.json) · [사전 시험 사례](contracts/family-v1.cases.json) |
| NIM 요청·도구 선택 응답·도구 반환 형태 | [공급자 형식 예시](contracts/nim-tool-call.example.json) — 미호출 합성 예시 |
| 다른 조합의 입력·출력·실패 형태 | [9개 조합 계약](contracts/combinations.md) · [schema](contracts/mission.schema.json) · [정상·보류·실패 예시](contracts/mission-fixtures.json) |
| 프런트 데이터 형식 확인 | [research-v1 JSON Schema](contracts/research.schema.json) |
| 정상·변화·보류·실패 화면 연결 | [6개 예시 JSON](../playbooks/examples/research/fixtures.json) |
| 계약 예시를 코드로 다시 실행 | [로컬 리허설](../playbooks/rehearsal.md) |
| 선택 이유·도구 호출·검증 시각화 재사용 | [실행 흐름 컴포넌트](../design/agent-flow.md) |

## 공급자 형식과 서비스 형식

**공급자 응답 → 서버 측 adapter/validator → research-v1 → 화면**으로 연결한다. 프런트는 모델 원문이나 인증 정보 대신 검증된 서비스 데이터를 받는다. 공급자별 예외·도구 결과를 그대로 UI에 흘리지 않는다.

| 층 | 입력 | 출력 | 확인 수준 |
|---|---|---|---|
| NIM chat/tool calling | `model`, `messages`, `tools[].function.parameters`, `tool_choice`; 최소 연결은 `stream:false` | `choices[].message.tool_calls[]`의 `id/name/arguments`; 도구 결과를 `role:tool`, `tool_call_id`, 문자열 `content`로 돌려준 뒤 다음 응답 | 아래 공식 자료의 형식 확인; 선택 계정의 실제 tool call 확인; 새 합성 입력의 완료/보류와 검증 후 호출 중단 확인 |
| NAT 함수 | 등록된 함수의 typed input 또는 명시한 input schema | 해당 함수의 typed output; streaming 타입은 최종 output과 별도 | 고정 revision 공식 패턴 확인; 로컬 NAT 설치·기동 미실행 |
| 근거 조회 도구 | 리허설은 입력 식별자 `case`, `attempt`; 새 합성 입력은 goal과 기존/추가 근거 배열; 실제 도구는 미션의 query/filter 계약 필요 | 리허설은 `{id, source, topic, supported, quote}[]` | 합성 함수 실행; 실제 Retriever/MCP 검색 형식은 미확정 |
| 서비스 adapter | 목표·미션 입력·호출 한도, 검증된 도구 반환값 | `run_id`, 실행 모드, 관측 이벤트, 근거, 산출물, 한계, 다음 행동 | 프로젝트가 정의한 아래 계약; NVIDIA 표준이 아님 |
| 개발 스킬 | 개발자가 제공할 요구사항·대상 코드·설정·환경 | 수정된 구성/도구 코드·확인 절차 | 실행 API가 아닌 작업 지침; 스킬 설치만으로 도구가 생기지 않음 |

NIM의 `arguments`는 JSON **문자열**이므로 parse 후 허용 도구명·인자 schema를 검사한다. 도구 실행은 서비스가 담당하고, tool call ID에 대응하는 결과를 다음 모델 호출로 전달한다. `HTTP 200`이나 응답 문장만으로 도구 실행 완료를 판정하지 않는다. [NIM 1.15 function calling](https://docs.nvidia.com/nim/large-language-models/1.15.0/function-calling.html)

Hosted 경로의 예시는 `POST https://integrate.api.nvidia.com/v1/chat/completions`이며 모델·권한·tool calling 지원은 별도 확인한다. `stream:true`일 때 토큰 SSE가 제공되더라도 이것을 검증된 서비스 이벤트와 동일하게 취급하지 않는다. [Hosted 모델 API 예시](https://docs.api.nvidia.com/nim/reference/nvidia-llama-3_3-nemotron-super-49b-v1_5-infer)

NAT는 단순 async 함수를 `FunctionInfo.from_fn()`으로 감싸거나 입력·중간 출력·최종 출력 타입을 명시할 수 있다. 이 때문에 모든 NAT 도구의 출력이 같은 JSON이라고 가정하지 않는다. 등록 모듈/entry point와 설치 버전을 확인한 뒤 adapter를 연결한다. [고정 revision의 함수 문서](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-tools-and-functions/references/tools-and-functions.md)

출처 확인일: 2026-10-05. NIM container 1.15의 문서와 hosted 모델 API는 서로 다른 배포 경로이며 같은 지원 범위를 보장하지 않는다. NAT 자료 revision은 `c7e1162a1c7ff18bbd797e090a56cad97c281c92`; 실제 설치 패키지 버전의 schema 확인이 우선이다.

## research-v1 — 프런트가 사용할 최소 계약

| 필드 | 의미·화면 사용 |
|---|---|
| `schema_version`, `run_id`, `input_hash` | schema·실행·입력 구분; 다른 실행의 이벤트를 섞지 않음 |
| `mode`, `model_id`, `http_requests` | `mock/replay/live`와 모델·호출 수를 명시; mock은 모델 null·HTTP 0 |
| `input` | 이 리허설의 goal·case 식별 문자열·limits; 실제 미션 도메인 입력으로 바꾸면 schema도 버전 변경 |
| `status` | `running/completed/partial/failed/cancelled`; `partial`은 보류로 표시 |
| `events[]` | seq 순서의 decision/tool/validation/result, 상태·짧은 이유·도구·시도·오류·근거 ID |
| `evidence[]` | 예시 근거의 ID·출처·주제·값·인용; 실제 자료와 구별되는 `fixture://` 주소 |
| `artifact` | 검증 후 확정 요약·근거 ID; 보류/실패는 null |
| `limitations`, `next_action` | 확인하지 못한 범위와 다음 행동 |

Schema 검사는 형식만 확인한다. 서비스 검증기는 근거 ID의 존재·중복, 출처 구분, 주제·값 일치, 완료 조건을 별도로 확인한다. 리허설의 '두 출처 일치'는 예시 판정 기준이며 실제 도메인의 정확성 기준을 대신하지 않는다.

판단 이벤트의 label은 실제 선택과 코드 종료를 구분한다. `모델의 도구 선택`은 모델이 현재 허용된 도구를 고른 기록이고, `실행 제어의 종료`는 검증·자료 소진·재시도 상한에 따라 코드가 결정한 종료다. 코드 종료에는 모델 요청을 추가하지 않는다. 상세 제어와 새 입력 사용법은 [리허설](../playbooks/rehearsal.md#관측-기반-실행-제어와-새-입력)을 따른다.

이벤트의 `completed`는 그 단계의 완료다. 도구 응답 수신만으로 전체 실행을 완료 표시하지 않으며 `validation`과 최종 `status`를 함께 사용한다. 보류/실패에서도 이미 확인한 근거는 유지하되 확정 산출물은 표시하지 않는다. 취소는 보류 색상에 '취소됨'과 다음 행동을 별도 표시하며, 현재 리허설은 취소 실행을 구현하지 않는다.

현재 UI는 저장된 전체 JSON을 읽고 이벤트를 순서대로 **예시 재생**한다. 서비스 endpoint·SSE·polling은 구현하지 않았다. 실제 비동기 연결 시 adapter에서 `run_id + seq`로 중복·역순·다른 실행을 처리하고, 누락된 최종 결과를 성공으로 추정하지 않아야 한다. 실행 중단과 화면 재생 일시정지는 다르다.

오류 분류는 `invalid_input / unavailable / timeout / rate_limited / invalid_output`; 공급자 HTTP 상태를 adapter에서 분류한다. 이 리허설이 주입하는 호출 오류는 timeout이며 HTTP 오류 매핑 자체는 미검증이다. 준비 범위에 파일·영상·바이너리 도구가 추가되면 원문 데이터를 이벤트에 넣지 말고 형식·위치·출처의 artifact 계약을 따로 정한다.

## 선택할 개발 스킬

| 스킬 | 먼저 제공할 것 | 받아서 확인할 것 |
|---|---|---|
| [nat-agent-configuration](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/SKILL.md) | 관측에 따른 선택 필요성, 도구 schema, 모델 지원 정보 | agent 설정·선택 이유; 작은 요청에서 실제 선택/종료 |
| [nat-tools-and-functions](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-tools-and-functions/SKILL.md) | 함수 입력/출력, 실패 분류, 버전과 등록 방식 | 등록된 함수·schema·작은 정상/실패 테스트 |
| [nvidia-ui](../../.agents/skills/nvidia-ui/SKILL.md) | 위 서비스 계약과 fixture, 필요한 사용자 과업 | 확정 토큰/상태를 재사용한 화면·키보드/상태 확인 |
| [agent-rubric](../../.agents/skills/agent-rubric/SKILL.md) | 구현 버전·실행 모드·입력/출력·검증 근거 | agent-v2의 7항목·관문·미확인·다음 개선; 프런트는 frontend-rubric으로 별도 평가 |

## 다른 조합으로 확장할 때

각 조합마다 공급자 **제품/버전/출처 → 요청 schema → 응답/오류/비동기 형태 → 서비스 adapter → 정상·보류·실패 fixture → 검증 기준 → 실행 확인 수준** 순서로 추가한다. 기존 서비스 공통 필드는 유지하되 도메인 결과를 억지로 같은 형태에 넣지 않는다. 실제 provider 출력 검증이 끝나기 전에는 frontend fixture와 실제 연결 성공을 구분한다.
