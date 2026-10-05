# 평가·프로젝트 분석 작업 가이드

## 1. WHAT — 역할
내부 점수와 Bio-3의 관찰 증거를 관리한다. 공식 심사 원인과 내부 추정을 분리한다.

## 2. CONTENTS — 파일과 기술
- README.md — 흐름·루브릭·평가 스킬 진입
- rubric.md, rubric.json — 항목/가중치
- ../../.agents/skills/agent-rubric/SKILL.md — 근거 기반 반복 평가
- scoring-guide.md — 관찰 증거·채점·개선 우선순위
- bio3-review.md — 예선 강점·한계와 본선 적용 원칙
- templates/ — 빈/예시 채점표·사례

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
배점 변경 시 rubric version을 바꾸고 score.py/test_score.py 호환성을 확인한다. 실행 모드와 코드 버전을 함께 기록한다.

## 4. HOW NOT — 주의할 함정
- 과거 13/20 또는 6/6을 현재 본선 성능으로 바꾸지 않는다 — 코드/입력/환경이 다르다.
- 실행 실패를 분모에서 빼지 않는다 — 가용성을 숨긴다.

## 5. WHERE — 의존성과 경계
score.py는 이 영역의 JSON을 읽는다. playbooks의 실제 결과가 평가 근거다.

## 6. WHY — 배경
본선 진출의 정확한 심사평은 없다. 자료 기반 잠정 평가는 개발 우선순위를 위한 도구다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_
