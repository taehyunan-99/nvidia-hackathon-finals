# 스킬 탐색: 도메인 → 작업 목적 → 개별 스킬

원본 정보는 [skills-index.json](../skills-index.json) 한 곳에 있다. 이 문서들은 검색용 자동 생성 뷰다. 공식 분류는 `categories`, 이 프로젝트의 도메인/작업 분류는 `domains/functions`에 구분했다. 작업 분류는 이름·설명에서 만든 탐색 보조이며 제품 지원 보증이 아니다.

| 도메인 | 고유 스킬 수 | 바로 읽기 |
|---|---:|---|
| 문서·검색·지식 | 6 | [knowledge](domains/knowledge.md) |
| 에이전트·평가·정책 | 34 | [agents](domains/agent-workflows.md) |
| 영상·이미지·비전 | 88 | [vision](domains/vision.md) |
| 음성·대화 | 8 | [speech](domains/speech.md) |
| 경로·수학 최적화 | 8 | [optimization](domains/optimization.md) |
| 생명과학·의료 | 29 | [biology](domains/biology.md) |
| 표 데이터·분석 | 4 | [data](domains/data.md) |
| 로봇·물리·시뮬레이션 | 72 | [robotics](domains/robotics.md) |
| 모델 학습·조정 | 72 | [training](domains/training.md) |
| 배포·서빙·인프라 | 102 | [infrastructure](domains/infrastructure.md) |
| GPU 개발·고급 계산 | 23 | [compute](domains/compute.md) |

## 기능으로 바로 찾기

`python3 scripts/lookup.py --kind skill --function evaluate --limit 8`처럼 도메인 없이 기능만 검색할 수도 있다.
각 스킬은 여러 도메인/기능에 연결될 수 있으므로 표의 합계는 고유 스킬 수와 다를 수 있다. 전체 범위는 NVIDIA/skills 398개 + NAT 11개다. 모든 NVIDIA 제품 저장소의 모든 비공개/미등록 스킬까지 포함하는 목록은 아니다.
