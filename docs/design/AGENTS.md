# 디자인 문서 작업 가이드

## 1. WHAT — 역할
UI 선택과 실제 디자인 스킬의 위치를 안내한다.

## 2. CONTENTS — 파일과 기술
- README.md — 스킬/시안/결정 기록 안내
- agent-flow.md — 도구 선택·분석 과정 컴포넌트 사용법
- design-decisions.json — 확정값·이유·적용 조건, 확정 상태 묶음과 미정 범위

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
디자인 세부 규칙은 canonical nvidia-ui 스킬에서 수정한다. 선택은 디자인 결정 JSON으로 관리한다.

## 4. HOW NOT — 주의할 함정
- 예선 3D/HER2 화면을 새 미션의 필수로 두지 않는다 — 실제 사용자 과업이 다르다.

## 5. WHERE — 의존성과 경계
실제 서비스 기능은 ../product/README.md를 따른다. ../../design/의 시안과 ../../.agents/skills/nvidia-ui/ 원본을 연결한다. 구현된 React 화면의 파일·검사·mock 경계는 ../../frontend/README.md에서 확인한다.

## 6. WHY — 배경
요소별로 확정한 값은 design-decisions.json에 누적하며, 기록되지 않은 스타일은 비교용 임시값이다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_
