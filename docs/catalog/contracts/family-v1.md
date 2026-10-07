# family-v1 — 가족 조건 검증과 에이전트 계약

상태: 사용자 요청으로 정의한 구현 기준 계약과 합성 시험 사례. 검증기·제품 에이전트의 구현 또는 시험 통과를 뜻하지 않는다. 요구사항 원본은 [PRD F01–F09](../../PRD.md), 역할 경계는 [ARCHITECTURE](../../ARCHITECTURE.md#논리-구성과-책임)다. 기존 research-v1과 프런트 mock 계약을 대체한 실제 API가 아니라 두 담당자의 병행 개발 기준이다.

형식 원본: [JSON Schema](family-v1.schema.json). 시험 입력과 **미리 작성한 정답**: [시험 사례](family-v1.cases.json). 스키마의 `validation_input`, `validation_output`, `search_input`, `search_output`, `detail_input`, `official_input`, `detail_output`, `question_card`, `resume_input` 정의를 각 생산자·소비자가 사용한다. 상세와 공식 보충 도구는 같은 detail_output 반환 형식을 쓰고 출처 registry의 종류로 구분한다.

## 책임과 신뢰

| 생산자 → 소비자 | 책임 |
|---|---|
| 웹 선택 카드 → 서버 | 허용된 선택값만 전달. `as_of`, 출처 허용 목록, 예산, 소유권을 브라우저가 지정하지 않음 |
| 서버 adapter → 검증기 | 날짜·가족 정보를 정규화하고 작업/조건 revision과 신뢰된 출처 목록을 연결 |
| 조회 도구/근거 정규화 → 검증기 | 후보별 원문 인용·위치·조회 시점·적용 대상과 구조화된 사실 제공 |
| 검증기 → 에이전트 | 조건별 판정·이유·근거·누락/충돌과 다음 확인의 종류 반환. 모델 호출이나 자료 조회를 직접 하지 않음 |
| 에이전트 → 실행 제어 | 관측에 따라 도구·질문·대안·종료 선택. 검증 결과·예산·권한을 임의 변경하지 않음 |
| 실행 제어 → 화면 | 검증된 후보/제외/확인 필요와 실제 이벤트만 전달 |

`trusted_source_ids`는 서버의 출처 registry에서 제공하는 값이다. 모델이 배열에 임의 ID를 넣어 권한을 얻을 수 없다. 증거의 `source_id`는 이 목록 안에 있어야 하며, 후보 ID·인용 위치·원문과 연결된다. `facts`는 원문에서 정규화한 주장이고 사실 인증 그 자체가 아니다. 운영용 정규화 계층은 인용과 값의 대응을 확인해야 한다. 출처 없는 주장·잘못된 형식은 입력 계약 오류로 거부하며 업무 판정을 생성하지 않는다.

원문 속 명령은 자료다. source ID에서 URL을 해석하는 것은 서버의 책임이며 임의 URL·외부 redirect·금지 경로를 모델 인자로 받지 않는다. 이 계약은 파일/네트워크의 실제 OpenShell 정책 검사를 대신하지 않는다.

## 입력 의미

- `request_id`, `conditions_revision`, `candidate_id`는 모든 판정·도구 결과·재개에 연결한다. `as_of`는 서버가 설정한 `Asia/Seoul`의 시각이다. 운영 날짜와 접수 기간을 별도로 저장한다.
- 운영 기간·회차·요일은 `visit_date`와 비교하고 접수 기간은 `as_of`와 비교한다. 방문일이 접수 종료일 뒤라는 이유만으로 부적합으로 만들지 않는다. 접수중 상태도 원문의 조회 시점에 한정하며 실시간 잔여석을 확정하지 않는다. 개별 회차의 신청 마감 같은 추가 조건을 정규화하지 못했다면 전체 booking 판정을 확정하지 않고 보충 확인으로 남긴다.
- `conditions.children=null`은 가족 정보 미입력이다. 자녀별 `grade`와 `age_years`는 각각 미확인일 수 있으며 **학년에서 만 나이를 계산하지 않는다**. 연령 범위가 제한을 걸치면 미확인이다.
- `composition_complete=false`이면 명시한 자녀 외 동반자를 임의로 없다고 보지 않는다. 보호자 `2+`는 `{minimum:2, maximum:null}`로 표현하며 정확히 2명으로 해석하지 않는다. 인원 상한·정확한 동반 조건에는 추가 확인이 필요할 수 있다.
- 관심 분야·지역은 기존 선택값을 사용한다. `visit_date=null`이어도 탐색을 시작한다. `delivery_mode=null`은 대면·온라인을 지정하지 않았다는 뜻이다. 명칭·좌표로 대면을 추정하지 않는다.
- `facts` 각각은 적용 대상 `child/family/session`과 `scope_match=applicable/not_applicable/unresolved`를 가진다. `not_applicable` 주장은 판정에서 제외하고 근거로 남긴다. 적용 범위가 불명확하면 임의로 우선시하지 않는다.

`frontend/src/contract.ts`는 현재 프런트 전용 제안이다. `grades`는 선택한 학년 종류이며 자녀 수/나이가 아니다. adapter는 이 정보로 정확한 가족 구성을 만들지 않는다. 최종 화면 카드 옵션과 후보 개수·정렬은 PRD의 미결정 범위를 유지한다.

## 검증 출력과 종합

조건별 고정 키는 `age`, `grade`, `companions`, `visit_date`, `booking`, `delivery`, `interest`다. 각 항목은 `suitable/unsuitable/unknown`, 이유 코드, 근거 ID를 반환한다. 근거 없이 `suitable`을 만들지 않는다. 제한 없음도 그 의미의 명시적 근거가 필요하다.

| 상황 | 기대 판정 |
|---|---|
| 적용되는 제한과 모든 입력 대상이 일치 | 해당 조건 `suitable` |
| 입력된 필수 조건에 명시적 불일치 | 해당 조건 `unsuitable` |
| 필요한 사용자 정보 또는 적용 근거가 없음 | 해당 조건 `unknown` |
| 같은 대상·시점의 적용 주장들이 모순 | `unknown`과 `conflicting_evidence`; 최신/상세/엄격한 문구를 자동 정답으로 선택하지 않음 |
| 운영 기간 안이지만 선택 날짜가 회차/요일과 불일치 | `visit_date=unsuitable` |
| 운영 기간만 있고 실제 회차/요일 자료 없음 | `visit_date=unknown`; 접수 기간으로 채우지 않음 |
| 접수종료·예약마감·취소 | `booking=unsuitable`; 신청 가능한 추천에서 제외 |
| 접수중 | 조회 당시 `booking=suitable`; 잔여석·예약 성공은 항상 `unverified` |

`overall`은 하나라도 `unsuitable`이면 `unsuitable`, 불일치 없이 하나라도 `unknown`이면 `unknown`, 모든 조건이 `suitable`일 때만 `suitable`이다. 명시적으로 요청하지 않은 delivery 조건은 운영 형태를 숨기지 않는 전제에서 `not_requested`로 통과할 수 있다. 나머지 참여조건의 누락을 not_requested로 덮지 않는다.

한 자녀라도 명시적으로 연령/학년 제한에 어긋나면 부적합이다. 알려진 자녀는 모두 맞지만 가족 구성이 불완전하면 전체 가족 적합성을 확정하지 않는다. 인원 판정에는 자녀·보호자 총원이 필요한 경우가 있으며 보장 가능한 범위 전체를 비교한다.

`needs`는 `user_input/detail/official_source/alternative`와 해당 조건을 반환한다. 이것은 강제 도구 순서가 아니다. 예산·허용 출처·현재 관측에 따라 에이전트가 다음 행동을 고르고, 실행 제어가 다시 인자와 권한을 검사한다.

이유 코드는 schema의 `check.reason_code` enum을 공유한다. `matched/explicitly_unrestricted/not_requested`, `missing_user_input/missing_source_fact/partial_composition`, `conflicting_evidence/scope_unresolved`, 명시적인 조건 불일치와 범위 모호성을 구분한다. 잘못된 날짜/범위·근거 참조·후보/출처 연결은 업무상 unknown으로 반환하지 않고 계약 오류로 거부한다. 날짜 포맷 검사는 format checker를 활성화하고, 범위의 minimum≤maximum 및 기간의 start≤end는 별도 의미 검사로 강제한다.

## 도구 계약

| 도구 | 입력과 반환 | 범위·오류 |
|---|---|---|
| `search_experiences` | 조건 revision, 관심/지역, 서버가 발급한 cursor, page size → 후보 ID·다음 cursor·조회 범위·coverage | 결과에 `ok/empty/error/policy_denied` 구분. 운영 날짜를 접수 날짜로 검색하지 않음. 필터를 조용히 완화하지 않음 |
| `get_experience_detail` | 현재 실행이 조회한 후보 ID → 후보의 상세 원문·근거·정규화 사실 | 다른 후보의 조건을 섞지 않음. timeout/잘못된 응답은 자료 없음과 구분 |
| `read_official_source` | 서버가 허용하고 현재 후보와 연결한 source ID → 보충 원문·조회 시점·적용 대상 | 임의 URL 금지. 근거 충분이면 호출하지 않아도 됨 |
| 검증기 | validation_input → validation_output | 순수 판정 계층. 형식 오류와 업무상 미확인을 구분 |

`coverage`는 `sample/bounded/complete_for_query`다. 공개 sample 첫 5건은 항상 sample이며 전체 서울 문화체험 목록으로 해석하지 않는다. page size·page 한도는 실행 설정으로 전달하고, cursor는 조건 revision에 묶는다. `next_cursor=null`만으로 전체 조회 완료를 주장하지 않는다. complete_for_query는 해당 query의 전체 범위를 확인한 도구 adapter만 설정한다. 한도 도달은 `limited`이며 전역 후보 없음이 아니다.

## 질문과 재개

질문 카드는 `question_id`, `request_id`, `conditions_revision`, `field`, 허용 `options[{id,label}]`를 가진다. 자유 텍스트로 우회하지 않는다. 답은 `resume_input`의 `selected_option_id`로 전달한다. 서버는 현재 작업 소유권·질문 ID·허용 option·revision을 검사하고, 답을 반영한 **새 revision**을 만든다.

오래된 revision의 답과 다른 작업의 답은 거부한다. 새 revision에서는 영향받는 판정을 다시 실행한다. 기존 근거는 적용 범위·조회 시점이 유효할 때만 재사용하며 예전 판정/검색 cursor를 새 조건의 결과로 표시하지 않는다. 카드로 표현할 수 없는 답은 미확인과 공식 확인 경로로 남긴다.

## 작업 종료와 허용 행동

| 관측 | 허용되는 의미상 행동 |
|---|---|
| 필요한 근거·입력이 충분하고 적합 후보 있음 | 검증된 추천으로 종료; 추가 조회는 필요성/이득을 설명해야 함 |
| 사용자 정보 부족 | 질문 카드 또는 미확인 후보와 함께 보류; 질문을 강제로 탐색 시작 조건으로 만들지 않음 |
| 자료 부족 | 상세/허용 공식 보충 조회 또는 확인 필요로 종료 |
| 적용 근거 충돌 | 범위 확인·공식 보충 조회 또는 충돌을 보존하고 보류 |
| 현재 후보가 필수 조건에 부적합 | 필수 조건을 유지한 재검색 또는 조회 범위 내 후보 없음/보류 |
| 조회 장애·정책 거부 | 제한된 재시도/부분 결과/실패; empty로 바꾸지 않음 |
| 예산·시간·단계 상한 도달 | 확인한 결과와 미확인을 분리해 limited 종료; 종료 뒤 추가 호출 금지 |

시험은 단일 도구 호출 순서를 정답으로 강제하지 않는다. 사례의 `allowed_actions`는 합리적 결과 경로, `preferred_actions`는 비용·질문 부담 비교를 위한 선호 경로다. 정책 거부·확정되지 않은 조건 변경·근거 없는 추천은 언제나 금지한다.

## 사전 시험과 기준선 비교

사례 파일은 공통 `base_input`과 사례별 `patch`를 가진다. 객체는 재귀 병합, 배열은 교체, **null은 미입력 값 자체로 유지**한다. 필드 삭제는 별도 `omit_paths`를 사용한다. 기대값은 구현 검증기에서 생성하지 않는다. 단일 후보 사례의 `base_agent_context`는 합성된 한 후보 query의 전체 조회 완료 상태이며, 부적합 후보 하나를 보고 전체 서울에 후보가 없다고 주장하는 계약이 아니다.

`expected`는 `checks`의 달라진 항목과 `reason_codes`, `overall`, `allowed_actions`, `preferred_actions`, `forbidden`을 가진다. 명시하지 않은 조건별 기대 판정은 baseline_expectation의 값을 유지한다. baseline_output은 정상 출력 형식의 독립 예시다. 오류 사례는 판정 대신 error만 생성해야 한다. 작업/도구/재개 사례는 해당 별도 schema와 기대 응답을 사용한다. 원자료는 모두 합성이며 실제 API 운영 상태의 정답으로 쓰지 않는다.

현재 31개 검증 사례와 11개 에이전트/재개 사례를 정의했다. 구조·ID 참조·합성 기대값의 형식은 `python agent/contracts/check_contract.py`로 확인한다. 이 명령의 통과는 가족 판정 알고리즘의 통과가 아니다.

비교 기준선은 같은 고정 자료·입력·허용 출처·호출/시간/단계 예산에서 **검색→후보 상세 한 번씩→같은 검증기**를 사용한다. 사용자 정보가 없으면 같은 질문 카드 계약을 사용할 수 있지만 보충 조회·대안 검색은 고정 순서에 추가하지 않는다. 기준선도 검증기의 미확인을 적합으로 바꾸지 않는다.

검증기 담당은 validation_input/output과 V01–V31을 구현 기준으로 사용한다. 에이전트 담당은 같은 계약의 합성 결과를 사용해 도구·분기와 A01–A07을, 서버 담당은 R01–R04의 소유권·재개 검사를 구현한다. 단계별 통과를 분리하고 합성 에이전트 분기를 실제 모델의 판단 변화로 채점하지 않는다.

측정값은 잘못된 적합 추천, 올바른 부적합/미확인, 과도한 보류, 불필요한 조회, 질문 카드 수, 실제 모델·자료 요청 수(재시도 포함), 전체 실행시간이다. 정상·실패 시도를 모두 포함하고 같은 cache 조건을 적용한다. 합성 시험 통과 뒤 같은 계약을 샌드박스에 연결해 live 경로·정책·키 비노출을 확인한다. 기준선 대비 이득은 측정 전 주장하지 않는다.
