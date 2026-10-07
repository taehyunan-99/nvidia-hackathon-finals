# 두루 — NVIDIA Hackathon Finals

한국 가족이 관심 있는 문화 분야에서 함께할 체험을 발견하고 후보를 비교·선택하도록 돕는 본선 서비스다. 초기 범위는 서울의 전통문화·역사 체험이며, 연령·동반 조건·날짜를 공식 근거와 대조한다. 목적과 제외 범위의 원본은 [INTENT](docs/intent/INTENT.md)다.

[공개 프런트 열기](https://d25wpps17lj0dn.cloudfront.net/) — 현재 합성 예시 화면이다. React 프런트·Docker/AWS 수동 공개, 모델 없는 AWS–Brev 연결 시험, 최소 OpenShell 보안 하네스가 구현돼 있으며 실제 에이전트·모델/API·공통 챌린지 완주는 아직 통합 전이다.

## 실행·검증

| 하려는 일 | 실행 방법과 경계의 원본 |
|---|---|
| 프런트 로컬 실행·빌드·화면 검사 | [frontend/README.md](frontend/README.md): Node.js 22.18+, 설치·개발 서버·Node/Playwright 검사 |
| 두루 프런트 수동 배포·복구 | [Docker·AWS 운영](docs/playbooks/frontend-deployment.md): 기존 AWS 대상·원격 권한 필요; 소스 변경만으로 자동 배포되지 않음 |
| OpenShell 파일·반출·결과 회수 검사 | [하네스 사용법](docs/playbooks/openshell-harness.md): 정책 경로·합성 검사·실제 패키지/에이전트 통합의 남은 세 조치 |
| AWS–Brev 연결 시험 | [연동 절차](docs/playbooks/aws-brev-deployment.md): 모델 없는 작업 API·인증·경계·복구 검사 |
| 자료·모델 연결 전 점검 | [자료 근거](docs/product/data-sources.md) · [모델 한도](docs/playbooks/model-policy.md): 개발 호스트 관측과 sandbox 통합 구분 |

문서·가이드와 Python 단위 검사는 저장소 루트에서 실행한다(Python 3.11+).

```sh
python3.11 scripts/validate.py
bash scripts/sync-agents-md.sh --check
python3.11 -m unittest discover -s scripts -p 'test_*.py'
```

단위 검사는 합성 입력·가짜 도구를 사용하며 실제 모델/API/OpenShell 연결의 통과를 대신하지 않는다. 변경에 맞는 검사 선택은 [CI 원칙](docs/operations/ci-policy.md)을 따른다.

## 문서와 개발 안내

세부 문서 탐색은 [문서 지도](docs/README.md) 한 곳에서 관리한다. [제품 정의](docs/product/README.md), [단계별 계획](docs/plan.md), [공식 본선 미션](docs/operations/mission.md)과 [내부 평가](docs/evaluation/README.md)를 연결한다. 도구·스킬 검색 명령은 [카탈로그](docs/catalog/README.md)에서 확인한다.

제품 화면은 `frontend/`, 비교 시안은 `design/`, 준비·검증·시험 운영 코드는 `scripts/`에 있다. 에이전트 작업 규칙과 영역 지도는 [AGENTS.md](AGENTS.md), 팀 협업은 [CONTRIBUTING.md](CONTRIBUTING.md), 새 checkout의 hook 설정은 [가이드 참조 운영](docs/operations/guide-sync.md)을 따른다. CLAUDE.md는 AGENTS.md를 참조한다.
