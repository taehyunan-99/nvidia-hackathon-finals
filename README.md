# 두루 — NVIDIA Hackathon Finals

한국 가족이 관심 있는 문화 분야에서 함께할 체험을 발견하고 후보를 비교·선택하도록 돕는다. 초기 범위는 서울의 전통문화·역사 체험이며, 자녀 연령·동반 조건·날짜를 출처와 대조해 적합·부적합·확인 필요를 구분한다. 목적과 제외 범위는 [INTENT](docs/intent/INTENT.md), 기능 요구사항은 [PRD](docs/PRD.md)를 따른다.

[배포된 데모](https://d25wpps17lj0dn.cloudfront.net/) · [소스 저장소](https://github.com/taehyunan-99/nvidia-hackathon-finals) · [공식 미션과 제출 요건](docs/operations/mission.md)

## 미션과 현재 구현 범위

문화·역사·지역·여행의 여러 자료와 사용자 상황을 비교하고, 신뢰성을 판단해 실제로 쓸 수 있는 결과를 만드는 미션이다. 두루는 가족의 조건에 따라 후보 상세·공식 안내를 보충 조회하고, 근거가 부족한 조건은 확정하지 않는다. OpenShell 내부의 에이전트와 도구 실행으로 접근 경계를 유지하는 것이 필수이며, 가족 서비스와 공통 챌린지는 각각 검증한다.

| 경로 | 구현과 검증 범위 |
|---|---|
| 공개 프런트 | React 합성 예시 화면. 실제 모델·자료 조회·정책 집행의 데모가 아니다. |
| 가족 에이전트 | NAT 1.9.0 ReAct·등록 도구·조건 검증기·모델 호출 제어·CLI/API·live 프런트 연결 코드가 있다. [에이전트 안내](agent/README.md)에 실제 서울 sample·상세 조회 후 4개 제외·1개 미확인 종료가 기록돼 있다. 전체 검색·잔여석·예약 가능성은 보장하지 않는다. |
| 공통 챌린지 | 허용 자료 검색·읽기·근거 인용·초안 생성 CLI가 있다. 합성 검사는 통과했으나 실제 제공 패키지의 완주는 미검증이며, 이전 실패·단계 한도 종료를 성공으로 취급하지 않는다. |
| OpenShell | 모델 없는 합성 파일·결과 회수·반출 차단 검사가 기록돼 있다. 실제 모델/API·provider를 포함한 최종 정책의 통과를 대신하지 않는다. |

위 실행 기록의 상세 범위는 [에이전트 README](agent/README.md)와 [보안 하네스](docs/playbooks/openshell-harness.md)를 따른다. 이 README의 갱신만으로 실제 모델 재실행·공개 배포·챌린지 통과를 확인한 것은 아니다. 학습은 수행하지 않았으며 **학습 재현 절차는 해당 없음**이다. 추론은 NVIDIA hosted 모델을 `MODEL_ID`로 지정하며 Nemotron 3 Super 연결 설정과 제약은 에이전트 안내에 있다.

## 설치와 데모 실행

배포 URL: [두루 웹 데모](https://d25wpps17lj0dn.cloudfront.net/). 설치 없이 접속할 수 있으며, 로컬 실행과 실제 에이전트 연결은 아래 절차를 따른다.

저장소 전체를 checkout한다. 프런트는 Node.js 22.18+, 문서 검사는 Python 3.11+, 에이전트는 Docker로 빌드하는 Linux Python 3.12 환경과 NAT 1.9.0을 사용한다. 실제 실행에는 별도 OpenShell sandbox·NVIDIA 추론 credential·기존 예산과 대조한 일일 장부가 필요하다.

### 합성 화면 확인

```sh
git clone https://github.com/taehyunan-99/nvidia-hackathon-finals.git
cd nvidia-hackathon-finals/frontend
npm ci
npm run dev
```

`http://127.0.0.1:5173/?demo=1`에서 관심 분야 → 자녀 학년·보호자 → 날짜·지역 → 분석 → 추가 질문 → 후보·근거 비교를 확인한다. 예시 설정에서 자료 충돌·빈 결과·조회 실패·정책 거부·한도 종료를 선택할 수 있다. 합성 정책 거부 표시는 OpenShell 집행 증거가 아니다. 공개 데모도 현재 이 합성 모드다.

### 에이전트 이미지와 실제 가족 데모

저장소 루트에서 이미지를 빌드하고 HTTP 요청 없는 기본 실행을 확인한다.

```sh
docker build -f agent/Dockerfile -t finals-family-agent:runtime .
docker run --rm finals-family-agent:runtime python -m family_agent.run
```

실제 실행은 [에이전트 설치·환경·패키지 배치·웹 연결 절차](agent/README.md#실제-실행의-선행-조건)를 따른다. 운영자가 sandbox에 `FAMILY_PROJECT_ROOT`, `MODEL_ID`, provider credential, `MODEL_DAILY_LEDGER`, `MODEL_LEDGER_RECONCILED=yes`를 구성하고 effective policy를 확인한다. 실제 키·`.env`를 이미지나 입력 자료로 복사하지 않는다. 기존 sandbox·gateway·다른 작업의 장부를 변경하거나 초기화하지 않는다.

가족 요청 `{request_id, conditions_revision, conditions}`을 `/hackathon/input/family-request.json`에 실행 전 배치한다. `conditions`는 [family-v1 계약](docs/catalog/contracts/family-v1.md)을 따른다. 제품 정책 적용 후 **sandbox 내부**에서 실행한다.

```sh
python -m family_agent.run --live --request /hackathon/input/family-request.json --output /hackathon/output/family-result.json
```

웹 데모는 sandbox 내부의 단일 API worker와 운영자 포워딩을 구성한 뒤, 로컬 `frontend/`에서 `VITE_AGENT_MODE=live npm run dev`로 연결한다. API 기동·소유권·재개·결과 회수 방법은 [웹 연결](agent/README.md#웹-연결)을 따른다. 일반 사이트의 프런트/API/OpenShell 왕복은 별도 통합 확인이 필요하며, 이 명령만으로 AWS 공개 사이트가 교체되지 않는다. 공개·복구는 [Docker·AWS 수동 배포](docs/playbooks/frontend-deployment.md)를 따른다.

## 공통 챌린지 실행과 확인

[주최 측 챌린지](https://github.com/seriousran/k-culture-openshell-challenge)의 확인 버전은 `714e2e8d32f9b77e763a2458ca11b1270e80abf6`이다(2026-10-07 원격 main 재확인). 패키지의 지명·인물·기관·연락처·자격증명은 가상 데이터다. 실제 착수 시 변경 여부를 확인한다.

원본 `hackathon/` 전체와 요청을 별도 빌드 context에 배치하고 [Workload.Dockerfile](agent/Workload.Dockerfile)로 workload 이미지를 만든다. `input/restricted/secrets` 원본을 삭제하거나 대체하지 않으며, 요청 파일도 읽기 전용 input이 적용되기 전에 추가한다. 배치·모드 전환 절차는 [가족 MVP와 공통 테스트 실행](agent/README.md#가족-mvp와-공통-테스트-실행)을 따른다.

공통 요청은 `{request_id, task}`이며 가족 조건을 요구하지 않는다. [TASK.md](https://github.com/seriousran/k-culture-openshell-challenge/blob/714e2e8d32f9b77e763a2458ca11b1270e80abf6/TASK.md)의 연습 요청은 음식 제한·당일 운영 정보를 반영한 해외 방문객 반나절 문화 코스 **초안**이다. 공통 정책 적용 후 sandbox 내부에서 실행하고 추가 조건으로 다시 확인한다.

```sh
python -m family_agent.run --live --challenge --request /hackathon/input/challenge-request.json --output /hackathon/output/challenge-result.json --additional-condition '오후 1시까지 종료'
```

공식 산출물 형식은 자유이며, 현재 구현은 근거 인용·불확실성·관측·실제 모델 요청 수를 담은 `challenge-agent-v1` JSON을 사용한다. 종료 코드와 output을 함께 확인하고 실패·한도 종료를 완료로 바꾸지 않는다. 인용의 원문 일치를 검사하더라도 초안의 모든 의미적 주장이 검증되는 것은 아니다.

검증은 정상 과업·상충/오래된 자료 판단·새 추가 조건·금지 파일 접근·미승인 전송·자료에 섞인 지시 처리를 포함한다. 문서 속 발송/업로드 요구는 사용자 승인으로 취급하지 않으며, 초안 요청을 발송·게시·예약·결제 권한으로 확대하지 않는다. 현재 외부 쓰기 도구는 제공하지 않는다. 실제 제공 패키지 완주와 최종 정책의 경계 재검증은 남아 있다.

## OpenShell 정책과 권한 이유

| 정책 파일 | 적용 대상 |
|---|---|
| [agent/policy.yaml](agent/policy.yaml) | 가족 에이전트: 서울 자료 조회·NVIDIA 추론 |
| [agent/challenge-policy.yaml](agent/challenge-policy.yaml) | 공통 CLI: 허용 input 읽기·output 저장·NVIDIA 추론 |
| [agent/provider-profile.yaml](agent/provider-profile.yaml) | 전용 NVIDIA 추론 provider의 credential·endpoint 범위 |
| [scripts/openshell_harness/policy.yaml](scripts/openshell_harness/policy.yaml) | 모델/provider 없는 합성 경계 검사 baseline |

| 접근제어 | 허용 범위와 이유 |
|---|---|
| 읽기 | 런타임·코드·의존성과 `/hackathon/input`만 읽는다. 시스템 경로는 Python과 sandbox 실행에 필요하며 input은 업무 근거 조회용이다. input 원본 쓰기는 허용하지 않는다. |
| 쓰기 | 업무 결과는 `/hackathon/output`; `/tmp`와 `/dev/null`은 실행 임시 파일·표준 런타임 용도로 허용한다. |
| 금지 파일 | `/hackathon/restricted`, `/hackathon/secrets`를 허용 목록에서 제외한다. 파일을 보존한 상태에서 직접·간접 접근 거부를 검사한다. |
| 프로세스 | UID/GID 1000의 non-root와 Landlock `hard_requirement`를 사용한다. 코드·자료 도구도 sandbox 내부에서 실행한다. |
| 네트워크 | 아래 목적지·포트·method/path와 `/usr/local/bin/python3.12`만 허용한다. 공통 모드에는 서울 조회 권한이 없다. |
| 결과 회수 | 작업 소유권·writer 종료를 확인하고 크기·JSON·symlink 등 파일 형식을 검사한다. 모델이 주장하는 소유권이나 보안 이벤트를 신뢰하지 않는다. |

정책 파일 존재만으로 집행 성공을 판단하지 않는다. 최종 이미지·provider·effective policy를 대조하고 정상 조회와 실제 거부 로그를 확인한다. 파일 부재·DNS/인증 실패는 정책 거부 증거가 아니다. 설치 버전별 실행법과 정상 대조/거부/미수신 확인은 [보안 하네스](docs/playbooks/openshell-harness.md)에 있다.

### 외부 API·서비스와 허용 범위

| 서비스 | 범위·목적 |
|---|---|
| NVIDIA `integrate.api.nvidia.com:443` | `POST /v1/chat/completions` 추론만. 가족·공통 모드에서 사용자 요청과 허용 자료의 관측을 모델에 전달한다. 인증값·금지 파일을 결과에 저장하지 않는다. |
| 서울 `openapi.seoul.go.kr:8088` | 가족 모드의 `GET /sample/json/tvYeyakCOllect/1/5/` 공개 sample 5건 조회만. 전체 검색·인증키 기반 조회로 확대하지 않는다. |
| 서울 `yeyak.seoul.go.kr:443` | 가족 모드의 `GET /web/reservation/selectReservView.do` 공식 상세 안내 보충 조회만. 예약·결제는 수행하지 않는다. |
| AWS·Brev·OpenShell | 기존 AWS의 프런트 공개와 기존 Brev의 sandbox 실행·운영자 포워딩. [연동 절차](docs/playbooks/aws-brev-deployment.md)를 따르며 브라우저에 gateway credential을 전달하지 않는다. |
| 네이버 지도·화면 외부 연결 | 개발 서버의 선택적 지도 테스트에서 SDK·타일을 호출한다. 일반 화면에는 팀원 이미지·GitHub 링크가 있다. [프런트 안내](frontend/README.md)의 범위이며 위 에이전트 정책 권한에 포함되지 않는다. |

모델의 실제 HTTP 요청은 재시도 포함 실행당 40회·일일 4,000회·최소 간격 15초·출력 1,024토큰·판단 10단계·실행 900초를 기본으로 제한한다. 장부 공유 범위와 재시도/timeout은 [모델 호출 기준](docs/playbooks/model-policy.md)을 따른다. 한도 종료는 미완료/보류다.

## 평가·검증 절차

문서·가이드 검사는 저장소 루트에서 실행한다.

```sh
python3.11 scripts/validate.py
bash scripts/sync-agents-md.sh --check
```

코드 변경과 실제 통합은 다음의 관련 검사를 선택한다. 합성 입력·가짜 도구 검사가 실제 모델/API/OpenShell 통과를 대신하지 않는다.

| 대상 | 검사 |
|---|---|
| 준비 도구·호출 제어·하네스 | `python3.11 -m unittest discover -s scripts -p 'test_*.py'` |
| 에이전트·NAT 합성 graph | `docker run --rm finals-family-agent:runtime python -m unittest discover -s /opt/family-minimum/agent/tests` |
| 조건 검증기 | jsonschema가 설치된 환경에서 `python agent/contracts/check_validation.py` |
| 프런트 | `frontend/`에서 `npm run build`, `npm test`, `npx playwright install chromium`, `npm run test:browser` |
| 실제 실행 경계 | 같은 최종 sandbox·policy에서 정상 output·추가 조건·금지 접근·미승인 반출·키 비노출을 확인: [하네스](docs/playbooks/openshell-harness.md) |

공식 배점은 NVIDIA 에이전트 기술 40·실용성/혁신성 20·완성도 20·발표 10·동료평가 10이다. 내부 루브릭은 공식 예상 점수가 아니며, 해석과 불확실성은 [공식 미션](docs/operations/mission.md#8-공식-심사-배점), 검사 선택은 [CI 원칙](docs/operations/ci-policy.md)을 따른다.

## 제출·발표 안내

**2026-10-07 17:20 KST까지** 전체 코드·OpenShell policy·README가 포함된 GitHub 저장소, 실행 가능한 데모 URL 또는 실행 방법, 발표자료를 지정 Slack 제출 채널에 제출한다. 발표는 데모·영상 로딩 포함 **총 5분**이며 문제 정의·핵심 기능·실제 데모·권한 설계를 설명한다. 발표자료는 PDF/PPTX 또는 로그인 없이 열람 가능한 링크여야 한다. [공식 챌린지 제출 안내](https://github.com/seriousran/k-culture-openshell-challenge#프로젝트-제출)

현재 공개 URL은 합성 화면이며 실제 에이전트 데모를 대신하지 않는다. 이 기준 checkout에는 최종 발표자료가 포함돼 있지 않다. 제출 전 실행 접근·챌린지 완주·최종 정책 증거·발표자료를 확인하고 제출 코드와 맞춘다. 상세 기준은 [미션·제출 요건](docs/operations/mission.md#9-제출물과-5분-발표), 반복 점검은 [submission-check](.agents/skills/submission-check/SKILL.md)를 따른다.

## 문서와 개발 안내

세부 문서 탐색은 [문서 지도](docs/README.md), 확정 범위는 [제품 정의](docs/product/README.md), 진행 계획은 [단계별 계획](docs/plan.md), 도구·스킬 검색은 [카탈로그](docs/catalog/README.md)에서 확인한다.

제품 화면은 `frontend/`, 실제 에이전트는 `agent/`, 비교 시안은 `design/`, 준비·검증·운영 코드는 `scripts/`다. 에이전트 작업 규칙은 [AGENTS.md](AGENTS.md), 협업은 [CONTRIBUTING.md](CONTRIBUTING.md), 새 checkout의 hook 설정은 [가이드 참조 운영](docs/operations/guide-sync.md)을 따른다. CLAUDE.md는 AGENTS.md를 참조한다.
