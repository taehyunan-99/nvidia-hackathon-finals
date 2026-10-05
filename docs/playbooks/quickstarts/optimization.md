# cuOpt 첫 실행

## 먼저 분리

배송/배차는 routing API, 자원/일정은 LP/MILP 수학 모델이 후보이다. 같은 API가 아니다. Mac은 remote GPU server client로 두고 Linux GPU 환경의 CUDA/driver와 package 조합을 먼저 확인한다.

## 설치·최소 계산

[cuopt-install](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/cuopt-install/SKILL.md)에 따라 **하나만** 선택한다. 조사 당시 CUDA 12용 안내는 `pip install --extra-index-url=https://pypi.nvidia.com 'cuopt-cu12==26.2.*'`, CUDA 13용은 `cuopt-cu13`이다. 문서 스킬 version 26.10.00을 CUDA 12 package version으로 그대로 대입하지 않는다.

1. 별도 venv에서 설치하고 `python -c "import cuopt; print(cuopt.__version__)"`로 확인한다.
2. 경로 문제라면 `cuopt-routing-api-python`의 3개 지점/1대 예제를 실행하고 비용행렬·방문지·capacity를 명시한다.
3. LP/MILP라면 `cuopt-numerical-optimization-formulation`으로 변수/목적/제약을 정한 뒤 `cuopt-numerical-optimization-api`의 최소 예제를 실행한다.
4. 원격 REST를 선택하면 `cuopt-server-api-python`의 server 버전/주소/submit·poll 규격을 따른다.

## agent 연결과 검증

agent는 요청을 검증 가능한 제약 schema로 바꾸고 solver tool을 호출한다. solver가 infeasible이면 제약을 임의 삭제하지 않고 어떤 변경이 필요한지 사용자에게 돌려준다.
최종 계획의 모든 방문/자원 한도/시간창과 목적값을 원본 데이터로 재계산한다. solver status를 출력하지 않는 계획은 완료로 인정하지 않는다.

초기 입력은 5개 작업 이하로 잡고 연결 가능성을 먼저 확인한다. 실패 시 작은 규칙 baseline을 명시하고, 실제 NVIDIA solver 사용이 필수인지 미션 기준을 다시 확인한다.
확인 수준: 공식 설치/사용법 조사, GPU 계산 미실행.
