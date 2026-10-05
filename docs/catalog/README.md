# 도구·에이전트·스킬 탐색

프런트 연결용 [입출력 계약·schema·fixture](contracts.md)는 대표 조사 조합부터 제공한다. `lookup.py "입출력" --kind recipe`로 찾을 수 있다.

미션에서 시작하면 [조합 선택](../playbooks/README.md), 제품 이름을 알면 [도구 카드](tools.md), agent 형태가 고민이면 [에이전트 비교](agent-types.md)를 읽는다.

- `python3 scripts/lookup.py "문서"` — 관련 조합·도구·스킬의 상위 결과.
- `python3 scripts/lookup.py --show recipe:documents` — 구체적인 구성과 실행 문서.
- `python3 scripts/lookup.py "cuopt" --kind skill` — 설치 이름·고정 버전·원문.
- [전체 스킬 인덱스](skills-index.json): NVIDIA/skills의 skills/**/SKILL.md 398개 + NAT 11개, 총 409개.

검색은 로컬 metadata에서 동작하며 모델/API를 호출하지 않는다. 원문 전체·참조 파일은 인덱스에 포함하지 않으므로 사용할 때 [스킬 확보](../playbooks/skill-setup.md)를 따른다. 인덱스 완료는 소프트웨어 설치/실행 완료가 아니다.

분류형 탐색: [도메인 → 작업 목적 → 스킬](skills/README.md). 11개 도메인과 7개 작업 필터는 공식 metadata를 바탕으로 만든 프로젝트 탐색 뷰다.

원본 갱신과 분류 유지 방법은 [카탈로그 관리](maintenance.md)를 따른다.
