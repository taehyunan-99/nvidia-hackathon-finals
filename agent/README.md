# OpenShell 내부 가족 문화체험 에이전트

첫 다섯 건의 서울 공개 sample을 모델이 등록 도구로 조회하고, 실제 관측한 서비스·출처 ID로 종료하는 연결 시험이다. 기존 family_minimum 진단의 범위다. 제품·공통 실행은 아래 family_agent를 사용하며 전체 검색은 지원하지 않는다. `inspection_complete`도 참여 가능성이나 예약 성공을 뜻하지 않는다.

입력·출력·판정·재개 계약과 42개 사전 사례는 [family-v1](../docs/catalog/contracts/family-v1.md)을 따른다. `python agent/contracts/check_contract.py`는 계약 형식·참조와 기대값의 일관성만 확인하며 제품 검증기의 시험 통과를 뜻하지 않는다. 이 검사는 jsonschema가 설치된 로컬 Python 또는 NAT 환경에서 실행한다.

## 구성과 검사

NAT 1.9.0의 `react_agent`, typed 등록 함수, LangChain 모델 adapter를 사용한다. 모든 모델 HTTP 요청은 기존 `scripts/model_policy.py`의 공유 일일 예산·실행 예산·간격·429 재시도를 거친다. NAT 파싱 재시도도 같은 adapter를 호출하며 판단 단계는 최대 10이다. 모델 endpoint는 NVIDIA 공식 주소로 고정하고 redirect는 거부한다. 원문 추론과 인증값은 실행 결과에 저장하지 않는다.

저장소 루트에서 전용 Linux 이미지를 빌드한다. 빌드 context는 필요한 코드와 정책만 포함한다.

```sh
docker build -f agent/Dockerfile -t finals-family-nat:trial .
docker run --rm finals-family-nat:trial python -m unittest discover -s /opt/family-minimum/agent/tests
docker run --rm finals-family-nat:trial python -m family_minimum.run
```

기본 실행은 dry-run이며 자료·모델 HTTP 요청이 없다. 단위 검사는 합성 transport를 쓰며 NAT graph 검사는 실제 NAT 등록·ReAct 파싱·도구 관측·출처 검증을 시험한다. 이는 실제 모델·서울 API·OpenShell 집행 성공의 증거가 아니다.

## 실제 실행의 선행 조건

기존 `finals-bridge`의 `/opt/nvidia-finals-bridge`와 기존 sandbox·policy를 보존한다. 별도 프로젝트와 sandbox에서 설치 버전·effective policy·허용 endpoint/binary를 확인해야 한다. 기존 outbound 차단 policy를 그대로 쓰면 조회·추론이 실패한다. 신규 workload 정책의 최소 허용 범위는 운영자가 확인한 서울 공개 sample GET과 NVIDIA 추론 POST다. `policy.yaml`과 `provider-profile.yaml`은 해당 경로와 Python 실행 파일만 허용하는 검증 대상 초안이며, 실제 effective policy 확인 전에는 집행 성공으로 보지 않는다.

운영자는 `FAMILY_PROJECT_ROOT=/opt/family-minimum`, `MODEL_ID`, provider가 제공하는 `NVIDIA_API_KEY`, 기존 집계와 합산한 `MODEL_DAILY_LEDGER`, `MODEL_LEDGER_RECONCILED=yes`를 전용 sandbox에 구성한다. OpenShell은 이미지 ENV를 그대로 상속하지 않을 수 있으므로 프로젝트 경로를 실행 환경에도 명시한다. 일일 예산을 새 DB로 초기화하지 않으며 여러 sandbox는 동일한 집계 주체를 사용한다. 실제 키·전체 `.env`를 이미지나 input으로 복사하지 않는다. 모델 endpoint 고정 때문에 provider의 동일 endpoint credential 대체 여부도 확인한다.

```sh
env FAMILY_PROJECT_ROOT=/opt/family-minimum python -m family_minimum.run --live --output /hackathon/output/inspection-001.json
```

출력 경로는 `/hackathon/output` 하위의 새 파일로 제한한다. 빈 자료·조회 오류는 보류하고 출처 없는 완료·관측하지 않은 ID·임의 URL·종료 뒤 호출은 코드로 거부한다. 같은 도구의 중복 조회는 현재 실행의 관측을 재사용한다. 실제 정책 검증은 같은 이미지·sandbox에 존재하는 금지 control 파일을 대상으로 기존 `scripts/openshell_harness/probe.py`와 effective policy·집행 로그를 연결해 확인한다. 파일 부재·DNS 실패는 정책 거부로 처리하지 않는다.

원문 지침: [NAT 함수 등록](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-tools-and-functions/references/tools-and-functions.md), [ReAct 설정](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-agent-configuration/references/agents.md). 최종 API는 PyPI 1.9.0 배포 코드와 실제 이미지 검사로 대조한다.

## 가족 MVP와 공통 테스트 실행

`family_agent`는 같은 NAT ReAct/호출 제어를 사용하는 제품 실행 계층이다. 코드가 필수 초기 조회를 수행하고 상세·공식 보충 조회 후 PR #15의 `family_minimum.family_validator.validate(dict) -> dict`를 호출한다. 검증기는 검색·행동 선택을 하지 않는다. 모델은 관측에 따라 보충 조회·다른 후보·질문·검증된 종료를 선택한다. 실행 제어는 미관측 ID·출처 없는 적합·부적합 추천·미완료 검색의 전체 후보 없음 주장을 거부한다.

서울 공개 sample 5건만 사용한다. 평문 인증키 조회 권한을 확대하지 않는다. 원문의 정확한 상태·기간·제한·주제·요일 일부만 정규화하며 모호한 본문 조건은 미확인/적용 범위 미해결로 남긴다. 전체 문화체험 검색이나 실제 잔여석을 보장하지 않는다. 프런트 학년 선택은 가족 전체 인원·연령을 확정하지 않으므로 많은 후보는 확인 필요다.

```sh
python -m family_agent.run --live --request /hackathon/input/family-request.json --output /hackathon/output/family-result.json
python -m family_agent.run --live --challenge --request /hackathon/input/challenge-request.json --output /hackathon/output/challenge-result.json --additional-condition '오후 1시까지 종료'
```

제품 요청은 `{request_id,conditions_revision,conditions}`이며 conditions는 family-v1이다. 공통 요청은 `{request_id,task}`이고 가족 필드를 요구하지 않는다. 공통 결과는 근거 인용·불확실성을 포함한 초안 JSON이다. 근거 인용은 관측한 원문 부분 문자열 또는 관측한 줄 번호로 회수·검증하지만 초안의 모든 의미적 주장을 코드가 인증하는 것은 아니다. 24개·32 KiB 이하의 작은 자료 묶음은 코드가 먼저 읽어 전달한다. 큰 자료 묶음은 모델이 필요한 자료를 선택한다. 공통 모드에는 허용 input 검색/읽기와 검증된 종료 도구를 제공하며 전송·예약·결제·외부 업로드 도구는 없다.

원본 challenge 패키지의 input/restricted/secrets를 삭제하거나 대체하지 않는다. input은 실행 중 읽기 전용이므로 **요청 파일도 sandbox 생성 전에** 배치한다. 기본 이미지를 이 저장소에서 빌드한 후, 원본 패키지와 요청을 복사한 별도 context에서 `Workload.Dockerfile`로 workload 이미지를 빌드한다. context에는 `hackathon/`만 두고 `.env`·모델 키·SSH 키를 넣지 않는다. 예: `docker build -f agent/Workload.Dockerfile --build-arg BASE_IMAGE=finals-family-agent:runtime -t finals-family-agent:workload /tmp/family-workload`.

제품은 `policy.yaml`, 공통 모드는 `challenge-policy.yaml`을 사용한다. 같은 sandbox의 모드를 바꾸면 API worker를 먼저 정지하고 `openshell policy set <name> --policy <file> --wait` 후 effective policy를 확인한다. 하루 장부는 보존하며 모델 CLI/API를 동시에 실행하지 않는다. API는 단일 worker 안에서 실행 사이 호출 간격도 유지한다. 별도 sandbox·다른 개발자의 예산은 자동 합산되지 않으므로 기존 장부와 운영 집계를 대조해야 한다.

## 웹 연결

실제 API는 **OpenShell 안에서** `uvicorn family_agent.api:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log`로 실행한다. `POST /api/runs`, 소유권 확인을 거치는 `GET/DELETE /api/runs/{id}`, 질문 카드의 `POST /api/runs/{id}/resume`을 제공한다. 소유권 토큰은 요청 생성 시 서버가 발급하고 `X-Run-Owner`로 전달한다. 한 작업의 다른 revision·다른 소유자·허용되지 않은 질문 답은 거부한다. 결과는 worker 종료 후 실행별 output에 봉인하고 기존 하네스의 안전한 JSON 회수 함수를 통과시킨다. 작업은 메모리에서 관리하며 완료 후 30분 만료, 최대 32건·대기/실행 4건이다.

운영자 포워딩은 `openshell forward service <name> --target-port 8000 --local 127.0.0.1:8000`이며 브라우저에 CLI나 gateway 자격증명을 제공하지 않는다. 로컬 Vite `/api/runs` proxy가 같은 8000번 포트로 연결된다. `VITE_AGENT_MODE=live npm run dev`로 실제 모드를 선택하고 기본은 기존 mock이다. live 화면은 실제 실행 관측을 표시하며 모델 이벤트를 정책 집행 증거로 표시하지 않는다. AWS의 기존 공개 합성 사이트를 이 명령만으로 교체하지 않는다.

검사: 이미지에서 `python -m unittest discover -s /opt/family-minimum/agent/tests`; 검증기 사전 정답은 `python agent/contracts/check_validation.py`; 프런트는 `npm run build`, `npm test`, `npm run test:browser`. 단위 검사와 NAT 합성 graph, 실제 모델/자료 조회, OpenShell 정책 집행을 구분한다. Nemotron 3 Super에는 1,024토큰 제한 내 ReAct 응답을 위해 `enable_thinking=false`를 적용한다. [NVIDIA 모델 API](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-super-120b-a12b-infer).


## 팀원 CLI 연결 범위

팀원은 `from family_agent.challenge import ChallengeRuntime`과 `from family_agent.run import execute`를 그대로 사용할 수 있다. 공유 모델 adapter는 `family_minimum.register`, 등록 도구는 `family_agent.challenge_register`, 설정은 `challenge-workflow.yml`이며 `execute(runtime, 'challenge-workflow.yml', runtime.query)`로 실행한다. 기존 최소 CLI는 `python -m family_agent.run --live --challenge --request ... --output ... --additional-condition ...`이다.

요청은 `{request_id,task}`이며 추가 조건은 별도 문자열이다. 허용 input만 읽고 결과는 challenge-agent-v1의 action/draft/citations/uncertainties/sources/events/physical_model_requests를 반환한다. 한도 종료·실패에서는 draft와 citations가 비어 있을 수 있으며 완료로 바꾸지 않는다. API 가족 카드와 결과를 공통 요청에 강제하지 않는다. 종료 도구는 관측 source ID 또는 해당 관측 파일 경로와 원문 인용/줄 번호를 검증한 뒤 canonical source ID·quote로 반환한다.

NAT 등록·실행·종료와 검증기·호출 제어의 합성 검사는 통과했고, 실제 가족 탐색은 공식 sample과 상세를 읽어 4개 제외·1개 미확인으로 종료했다. **실제 챌린지 완주는 미검증**이다. 이전 실제 챌린지 시도는 초기 템플릿 오류 또는 읽기 반복·종료 검증 문제로 실패/10단계 한도 종료했으며 성공으로 사용하지 않는다. 최신 줄 번호 인용과 코드의 작은 자료 묶음 선조회는 합성 검사만 통과했다. 팀원은 실제 제공 패키지·새 추가 조건·정상 output·종료 코드·금지 접근/전송·원문 지시 처리·서버와 키 비노출을 확인해야 한다.

기존 Brev의 `family-agent-mvp` sandbox와 전용 모델 provider를 재사용할 수 있으나 실행 전 이미지·effective policy·예산 장부를 확인한다. 제품과 공통 모드를 동시에 실행하지 않는다. CLI에는 `challenge-policy.yaml`을 적용하고 일일 장부를 새로 초기화하지 않는다. 부모 프로젝트의 `/opt/nvidia-finals-bridge`와 기존 gateway·다른 sandbox·예선 저장소는 수정하지 않는다. 일반 사이트의 프런트/API/OpenShell 왕복과 공개 사이트 배포는 다음 프런트 세션의 담당이며 현재 공개 사이트는 합성 상태다. 웹 챌린지 화면·전용 API·모드 전환은 제거했다.
