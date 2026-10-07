# 디자인 비교 시안 작업 가이드

## 1. WHAT — 역할
확정한 컴포넌트와 상태 표시를 조합해 확인하는 데스크톱 정적 HTML.

## 2. CONTENTS — 파일과 기술
- playground.html — HTML/CSS/JS 비교 화면
- agent-flow.html, agent-flow.mjs — 계약 fixture를 읽는 실행 흐름 리허설

기술: Markdown/JSON 중심; scripts는 Python/Bash, design은 HTML/CSS/JavaScript.

## 3. HOW — 수정 방법
nvidia-ui 스킬을 읽고 확정값을 보존한다. 상태 묶음까지 확정했으며 미세 비교는 다시 시작하지 않는다. 브라우저에서 현재 비교하는 속성과 관련 상태를 확인한다. 모바일·태블릿 대응과 검사는 제외한다.

## 4. HOW NOT — 주의할 함정
- 가상 수치를 실제 agent 결과로 표현하지 않는다 — 비교 화면은 mock이다.

## 5. WHERE — 의존성과 경계
실제 서비스 범위는 ../docs/product/README.md가 원본이며 이 폴더의 시안은 구현 완료 근거가 아니다. ../.agents/skills/nvidia-ui/assets/의 tokens.css·components.css·agent-flow.css·agent-flow.mjs를 사용한다. 기본 데이터는 ../docs/playbooks/examples/research/fixtures.json이며 source=live는 runs/research-live.json의 저장 기록을 재생한다. 문서는 ../docs/design/에 둔다.

제품의 React 프런트는 ../frontend/에 있으며 실행·검사·임시 계약은 ../frontend/README.md를 따른다. 이 폴더의 정적 시안과 제품 프런트의 역할을 구분한다.

## 6. WHY — 배경
NVIDIA를 참고한 독립 디자인이며 로고/공식 제품 인증이 아니다.
알려진 사실/기존 결정만 기재했다. 추가 도메인 고유 함정은 사용자 확인 후 보완한다.

## 7. ⚠️ LEARNED CAUTIONS — 학습된 주의사항
명시한 `$learn`/`/learn`에서만 추가한다.

_(아직 없음)_
