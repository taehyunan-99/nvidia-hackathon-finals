# 가속 분석·서빙·Physical AI 선택

이 경로는 장비/데이터/문제 적합성이 먼저다. 'NVIDIA 사용'을 위해 일괄 설치하지 않는다.

| 목적 | 먼저 읽을 스킬 | 실행 순서 | 성공 판정 |
|---|---|---|---|
| 표 데이터 처리 | accelerated-computing-cudf | CPU baseline→지원 GPU 환경→스킬의 설치/연산 예제→동일 데이터 계산 | 결과 일치+전체 소요 시간 비교 |
| inference 병목 개선 | dynamo-recipe-runner, dynamo-router-starter | 이미 동작하는 endpoint→고정 부하→backend recipe→동일 부하 | 오류율·latency·throughput을 함께 비교 |
| 로봇 mission control | isaac-mission-control-showcase | simulator/scene/장치 조건→원문 demo→입력 변경→관측 | 미션 상태/행동과 실제 시뮬레이션 관측 일치 |
| 물리 영상 예측 | paidf-cosmos-predict | 데이터/모델/GPU 조건→원문 pipeline의 작은 입력→산출물 검증 | 형식·데이터 사용 범위·미션별 검증 가능성 |

각 스킬의 고정 원문은 `python3 scripts/lookup.py 이름 --kind skill`로 찾는다. 준비된 scene·GPU·기준선이 없으면 이번 미션의 핵심에 맞는 더 작은 경로를 먼저 만든다.
이 표는 빠른 탐색 경로이며 해당 제품의 독립 실행 매뉴얼을 대체하지 않는다. 설치/실행 가능성은 원문 조건과 제공 환경이 맞는지 확인한 뒤 판단한다.
확인 수준: metadata와 원문 탐색 경로; 장비 기반 실실행 미검증.
