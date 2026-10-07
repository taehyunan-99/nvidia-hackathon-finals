# OpenShell 내부 NAT 최소 연결

첫 다섯 건의 서울 공개 sample을 모델이 등록 도구로 조회하고, 실제 관측한 서비스·출처 ID로 종료하는 연결 시험이다. 가족 적합성 추천·전체 검색·상세/보충 조회·질문 재개는 아직 구현하지 않았다. `inspection_complete`도 참여 가능성이나 예약 성공을 뜻하지 않는다.

후속 병행 개발의 입력·출력·판정·재개 계약과 42개 사전 사례는 [family-v1](../docs/catalog/contracts/family-v1.md)을 따른다. `python agent/contracts/check_contract.py`는 계약 형식·참조와 기대값의 일관성만 확인하며 제품 검증기의 시험 통과를 뜻하지 않는다. 이 검사는 jsonschema가 설치된 로컬 Python 또는 NAT 환경에서 실행한다.

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
