# 주제에 덜 묶이는 에이전트 하네스

여기서 하네스는 미션이 바뀌어도 유지할 **입력 계약·실행 제어·검증·관측·평가의 틀**이다. 이번 단계는 설계와 준비 도구까지이며 범용 실행 에이전트를 완성한 상태는 아니다.

구체적인 프런트 연결은 [대표 입출력 계약](../catalog/contracts.md)과 [리허설](rehearsal.md)을 사용한다.

## 최소 구조

`입력 검증 → 상태/허용 도구 → 모델의 다음 행동 → 도구 실행 → 결과 검증 → 재시도/추가 조사/종료 → 근거 있는 산출물`

미션별로 바꾸는 것은 domain 입력, 도구 2~4개, 성공 판정기, 화면 결과 영역이다. 동일하게 유지할 것은 trace, 실행 모드, 예산, 오류 분류, run_id와 데이터 해시다. CLI/노트북/웹 어느 형태에도 적용한다.

| 경계 | 최소 계약 | 실패 처리 |
|---|---|---|
| 입력 | run_id, goal, input, input_hash, limits | schema 실패는 모델 호출 전 종료 |
| 도구 | 이름, 인자 schema, timeout, read/write 성격 | invalid_input / unavailable / timeout / rate_limited / invalid_output을 구분 |
| 관측 | tool, status, duration_ms, evidence_ids, output_hash | 빈 결과와 호출 실패를 다르게 기록 |
| 판단 | next_action, 짧은 이유 요약, evidence_ids | 근거 없는 수치/출처는 validator가 거부 |
| 결과 | completed / partial / failed / cancelled, artifact, limitations | 미측정 값은 null; 보류를 시스템 장애와 구분 |
| 실행 모드 | live / replay / mock, model_id, 실제 HTTP 횟수 | replay의 과거 provenance와 현재 run 분리 |

내부 추론 전문 대신 관찰 가능한 도구/상태/근거/짧은 결정 이유를 저장한다. 키·인증 헤더는 기록하지 않는다.

## 본선에서 우선 만들 요소

1. **계약 fixture:** 모델을 붙이기 전 정상·보류·오류 JSON을 서비스/UI가 읽게 한다. 도구와 화면 담당이 같은 run_id와 상태 이름을 쓴다.
2. **예산과 종료:** [모델 호출 운영 기준](model-policy.md)의 실행당 40회·일일 4,000회·10단계·900초와 429 최초 포함 3회 시도를 적용한다. 미션별 변경은 해당 정책과 런타임 연결에서 함께 관리한다. 429 대기가 남은 시간보다 길면 보류하고 기록한다.
3. **검증기:** LLM이 만든 답의 값·출처·단위·제약을 코드로 확인한다. validator가 확인한 범위만 완료로 표시한다.
4. **trace와 재생:** 원본 요청 해시·모델/버전·도구 상태·결과 파일을 남긴다. replay는 명시적으로 표시하고 다른 입력의 캐시를 재사용하지 않는다.
5. **작은 평가셋:** [평가 양식](../evaluation/templates/eval-cases.json)의 8개 유형을 미션에 맞게 채운다. baseline과 agent를 같은 조건에서 비교한다.

## 부작용과 병렬성

동일 작업 재시도는 멱등 키를 사용하거나 도구 결과를 먼저 확인한다. 네트워크 timeout은 서버가 작업하지 않았다는 뜻이 아니다. 외부 쓰기 작업은 실제 미션 권한에 맞춰 별도 승인을 거치거나 sandbox에서 수행한다.
여러 worker가 같은 키를 쓰면 프로세스별 sleep만으로 호출 한도를 지킬 수 없다. 7시간 안에는 한 실행 worker/공유 호출 큐부터 시작하고, 독립적인 읽기 작업만 이득이 확인될 때 병렬화한다.

## 환경 전략

로컬 노트북은 UI/개발/평가를 맡고 실제 추론은 먼저 hosted API 가용성을 확인한다. GPU가 필요한 도구는 제공 Brev 환경에서 분리한다. Mac에서 CUDA가 없는 것을 전체 준비 실패로 보지 않는다.

`python3 scripts/preflight.py`는 설치 도구·Python·키 유무만 점검한다. 키를 출력하지 않으며 모델 호출/GPU 임대는 하지 않는다. 실제 연결은 다음을 따로 기록한다: 모델 tool-call 1회, 핵심 도구 1회, malformed 응답 거부 1회, 끝까지의 trace 1건. `.env.example`은 변수 이름 초안일 뿐 SDK가 자동으로 읽는다는 계약이 아니다.

## 재사용 범위 제안

Bio-3에서 **상태 관문, 근거 연결, 예산/복구 패턴**을 가져오되 HER2 서열·구조 스키마·전용 worker 전체를 범용 엔진으로 포장하지 않는다. 재사용 허용 여부는 온보딩에서 확인한다.
NAT의 [평가](https://docs.nvidia.com/nemo/agent-toolkit/latest/improve-workflows/evaluate.html)와 [관측/워크플로 문서](https://docs.nvidia.com/nemo/agent-toolkit/latest/index.html)는 다음 단계 도입 후보다. 버전 잠금과 작은 연결 시험 후 사용한다.
