# 평가·Guardrails·합성 데이터

## 가장 작은 평가

[evaluation/templates](../../evaluation/templates/eval-cases.json)의 정상/변화/누락/불가능/검색 실패/timeout/잘못된 응답/중복 사례를 미션에 맞게 채운다. 입력과 기대 결과를 실행 전에 고정하고 baseline/agent를 동일 조건으로 측정한다.

## NAT 평가

NAT 작업 프로젝트에서 `uv add "nvidia-nat[eval]==1.9.0"` 후 `uv run nat eval --help`로 설치 버전이 제공하는 옵션을 확인한다. `nat-evaluation`의 원문 데이터 형식/설정 예제를 복사·조정하고 `nat eval --config_file <평가설정.yml>`을 실행한다. [평가 원문](https://docs.nvidia.com/nemo/agent-toolkit/latest/improve-workflows/evaluate.html).
성공 기준: 정상과 실패가 모두 집계되고 각 점수가 해당 trace로 돌아가야 한다. `rag-eval`은 RAG Blueprint용 구조에만 사용한다. 모델 judge의 의견은 독립 계산/출처 검산을 대체하지 않는다.

## Guardrails

별도 호환 Python 환경에 `pip install nemoguardrails`. [공식 README](https://github.com/NVIDIA-NeMo/Guardrails)의 RailsConfig/LLMRails 예제와 정책 config를 사용하고 provider를 실제 endpoint로 연결한다. 규정상 허용/금지 요청 한 쌍을 먼저 시험한다. source-grounding·수치/권한 검증은 코드 validator와 함께 둔다.
`nemotron-policy-generator`는 정책 작성 보조 스킬이며 Guardrails 설치 전체를 대신하지 않는다.

## Data Designer

별도 호환 환경에 `pip install data-designer`. `data-designer` 스킬의 workflow를 따라 schema→생성→validator를 정의한다. [공식 시작 문서](https://docs.nvidia.com/nemo/datadesigner/getting-started/welcome).
먼저 5건만 생성해 schema·값 범위·의미를 직접 확인한 뒤 평가 입력을 확장한다. 생성 모델이 만든 답을 그대로 gold로 채택하지 않는다. API 비용/토큰 수는 수집되지 않았으면 unknown이다.

확인 수준: 공식 사용법 조사. 이 준비 폴더의 채점기 tests와 외부 모델 평가 성공을 혼동하지 않는다.
