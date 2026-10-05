# 미션에서 실행까지

공통 원리는 [에이전트 흐름](agent-flow.md), 평가 기준은 [루브릭·스킬](../evaluation/README.md)을 따른다. 운영 방향은 [2인 개발·로컬 시연](../operations/workflow.md), 검색부터 화면까지 점검은 [로컬 리허설](rehearsal.md)을 따른다.

1. [미션 카드](templates/mission.md)에 사용자·실패 상태·입력·성공 기준을 적고 [주제 선정 기준](../evaluation/topic-selection.md)으로 후보를 비교한다.
2. 선택한 주제에 [조합 선택표](recipes.md)를 적용하고 `python3 scripts/lookup.py "미션 핵심어" --kind recipe` 또는 아래 목록에서 한 조합을 고른다.
3. 해당 조합의 quickstart→스킬 확보→실제 한 건 실행→독립 검증 순서로 진행한다.
4. [평가](../evaluation/README.md)에 근거를 기록한다. 미션에 없는 기술을 점수를 위해 추가하지 않는다.

- [문서·규정 검토](missions/documents.md) — 3개 문서에서 인용 있는 검토표와 자료 없음 판정
- [조사·대안 비교](missions/research.md) — 두 출처를 비교하고 근거 충돌을 드러내는 보고
- [배송·배차·경로](missions/routing.md) — 5개 방문지의 제약을 만족하는 경로
- [자원·일정 최적화](missions/allocation.md) — 작은 작업 배분표와 목적값
- [장애·업무 처리](missions/operations.md) — 상태 조회와 근거 있는 다음 조치
- [영상 검색·검토](missions/video.md) — clip의 사건과 실제 시간 구간
- [음성 업무](missions/voice.md) — 발화→전사→업무 결과
- [분자·구조 검토](missions/biology.md) — 형식과 출처가 검증된 구조 결과
- [표 데이터 분석](missions/data.md) — 질문에 답하는 재현 가능한 표/계산
- [격리된 에이전트 운영](missions/sandbox.md) — 허용 영역에서 파일 작업 완료

직접 맞는 조합이 없으면 [전체 검색](../catalog/README.md)에서 전문 영역을 찾고 [하네스 계약](harness.md)에 맞는 작은 도구로 연결한다. 미션 목록은 예시이며 당일 주제를 미리 확정하지 않는다.
