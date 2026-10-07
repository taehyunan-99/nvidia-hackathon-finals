# GPU·격리 runtime 준비

## Brev

[대회 당일 사용 가이드](../brev-event-guide.md)에 API와 직접 GPU 운영의 선택 기준, 크레딧 등록, OS별 접속 명령, 백업·종료 절차를 정리했다.

[공식 시작 페이지](https://docs.nvidia.com/brev/getting-started/overview)에서 팀 계정/크레딧과 사용할 GPU를 확인한 뒤 환경을 만든다. 지급 정보·비용·종료 조건이 미확정인 현재 자동 임대하지 않는다.
연결 후 `nvidia-smi`, `docker version`, `docker info`로 장치/driver/daemon을 확인하고 GPU 컨테이너는 선택 제품의 image/tag·runtime 조건에 따라 시작한다. 접속 성공 이후 실제 모델/solver 한 건까지 별도로 기록한다. `tao-run-on-brev`는 TAO 전용이며 범용 Brev 설치 스킬로 쓰지 않는다.

## NemoClaw

`nemoclaw-user-guide`를 확보하고 [공식 문서 인덱스](https://docs.nvidia.com/nemoclaw/llms.txt)에서 선택한 agent variant의 prerequisite와 quickstart를 연다. OpenClaw/Hermes/Deep Agents 지침을 섞지 않는다.
순서: host 조건→provider→sandbox→허용 파일 작업→차단 동작→산출물. agent에게 주는 목표와 runtime 설정을 별도 기록한다. [공식 저장소](https://github.com/NVIDIA/NemoClaw).

## OpenShell

본선의 OpenShell 필수 조건과 외부 사용자 테스트 요구는 [v0.1.2 보안정책 분석](../../catalog/tools/openshell-security.md)·[배포 준비](../openshell-deployment.md)를 우선한다. 아래 일반 실패 대안은 필수 도구를 제외할 근거가 아니다.

[설치](https://docs.nvidia.com/openshell/latest/about/installation)와 [정책](https://docs.nvidia.com/openshell/latest/how-it-works/policies/overview)을 읽고 선택 환경에 맞는 CLI/runtime을 준비한다. `uv add openshell`은 Python SDK 경로이며 모든 daemon/host 배포가 끝났다는 뜻이 아니다.
읽을 파일 하나·허용 endpoint 하나로 시작해 허용/차단을 각각 확인한다. 외부 쓰기 작업은 실제 미션 권한과 멱등성 검사를 갖춘 뒤 연결한다.

## 실패 대안

운영 runtime이 핵심 미션이 아니라면 NAT+명시 도구 함수의 작은 경로부터 구현한다. host setup/이미지 다운로드가 시간 예산을 넘으면 해당 조합을 보류한다. 호스팅 권한을 설치 지침에서 자동으로 추론하지 않는다.
확인 수준: 조사. Brev 지급/임대·격리 runtime 설치·실행 미수행.
