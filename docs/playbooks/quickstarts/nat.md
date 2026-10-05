# 공통 첫 실행 — 모델 도구 호출과 NAT

## 선택/준비

선택 모델이 tool-calling을 지원하는지 실제 확인한다. hosted NIM은 로컬 GPU가 없어도 호출 가능하지만 계정 권한·쿼터는 별도다. 예선 환경의 `nvidia-nat==1.9.0` 설치를 확인했으며 이 폴더의 새 환경 검증을 뜻하지 않는다.

## A. SDK 설치 전에 API 계약 확인

Python 표준 라이브러리 보조 도구를 제공한다. 모델 ID와 키는 셸 환경변수로 제공하고 파일에 넣지 않는다.

```sh
python3 scripts/probe_nim.py
# MODEL_ID와 NVIDIA_API_KEY를 설정한 뒤, 실호출을 의도할 때만:
python3 scripts/probe_nim.py --live --output runs/nim-probe.json
```

기본 명령은 dry-run이다. live는 최대 두 HTTP 요청으로 덧셈 도구 선택→코드 실행→모델 최종 결과를 검사한다. 성공 기준은 도구 이름/인자/결과 검증과 JSON 결과 42 일치다. 텍스트 응답만 받으면 실패다. 401/403이면 권한, 404면 model/endpoint, 429면 한도 문제를 먼저 확인한다. API body·key·내부 추론은 기록하지 않는다.

본선 서비스의 호출 기본값은 [모델 호출 운영 기준](../model-policy.md)을 따른다. 아래 NAT 예제의 기본 provider만으로 물리 요청 수·일일 한도가 적용되지는 않으며, 실제 연결 시 공통 budget adapter를 연결한다.

## B. NAT 실행 환경

별도 작업 프로젝트에서 아래 명령을 사용한다. 루트 준비 자료를 애플리케이션으로 바꾸지 않는다.

```sh
uv init --python 3.12
uv add "nvidia-nat[langchain]==1.9.0"
uv sync
uv run nat --version
uv run nat info components
```

1.9.0을 구할 수 없거나 플랫폼과 맞지 않으면 [설치 원문](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-installation/references/installation.md)과 package 지원 범위를 확인한다. latest 문서가 다른 버전일 수 있으므로 임의 업그레이드 뒤 같은 API라고 가정하지 않는다.

## C. workflow 한 건

[예제 YAML](../examples/nat/workflow.yml)을 작업 프로젝트에 복사하고 `MODEL_ID`, `NVIDIA_API_KEY`를 환경에 설정한다.

```sh
uv run nat run --config_file workflow.yml --input "Use current_datetime to report the current date."
```

현재 날짜 문자열만 맞는 것으로 충분하지 않다. 도구 실행 trace에 `current_datetime`이 있고 반환값을 최종 답이 사용했는지 확인한다. 날짜 도구는 연결 시험이며 실제 미션의 가치 증거가 아니다.

## D. 미션 도구로 교체

`nat-tools-and-functions`를 읽고 함수의 입력 schema·반환 schema·실패 상태를 등록한다. [원문](https://github.com/NVIDIA/NeMo-Agent-Toolkit/blob/c7e1162a1c7ff18bbd797e090a56cad97c281c92/skills/nat-tools-and-functions/references/tools-and-functions.md). 함수 추가 시 설치된 패키지 entry point/등록 discovery와 YAML `_type`을 함께 확인한다. 함수 이름만 YAML에 적는다고 도구가 구현되지 않는다.

[에이전트 형태](../../catalog/agent-types.md)에서 필요한 분기만 선택하고, [하네스 계약](../harness.md)의 timeout·호출 상한·validator를 연결한다. MCP는 `nat-mcp-and-serving`에서 실제 서버 transport·tool schema·인증을 확인한 뒤 연결한다.

확인 수준: 예제·보조 도구의 오프라인 검사와 구성 검사, 본선 API 연결은 미실행.
