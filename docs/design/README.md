# 확정한 디자인 기준

- [80개 세부 기준과 상태 표시 묶음](design-decisions.json): decisions는 사용자 확정값·이유·적용 조건의 원본이며 그대로 보존한다.
- [디자인 스킬](../../.agents/skills/nvidia-ui/SKILL.md): 당일 재사용 절차와 범위.
- [토큰](../../.agents/skills/nvidia-ui/assets/tokens.css) · [컴포넌트 CSS](../../.agents/skills/nvidia-ui/assets/components.css): 버튼·입력·카드·표·기술 정보.
- [입력에 따른 시각 규칙](../../.agents/skills/nvidia-ui/references/activity-rules.md): 후보 수·ID·도구·이벤트를 링·색·배치·모션으로 변환하는 규칙.
- [도구 선택·분석 과정](agent-flow.md): 중앙 에이전트·도구 지도, 이벤트별 모션 규격, 당일 연결 순서와 6개 예시 재생.
- [팀원·GitHub 준비 규칙](../../.agents/skills/nvidia-ui/references/team-and-github.md) · [2인 프로필 데이터](../../.agents/skills/nvidia-ui/assets/team-content.json): 본선 역할·작업·링크는 당일 입력.
- [대표 데스크톱 화면](../../design/playground.html): 5개 상태를 한 화면에서 검토하는 가상 서비스. 기능·배치·주제 확정이 아니다.
- [확정 상태와 검증 기준](../../.agents/skills/nvidia-ui/references/quality.md): 5개 상태의 의미·표시·다음 행동.

디자인 준비는 확정·정리했다. 미세 색상·간격 비교는 종료하며, 80개 세부 기준과 진행·완료·보류·실패·빈 화면의 상태 묶음을 decisions에 보존한다. 개발·통합은 [2인 개발·로컬 시연 운영](../operations/workflow.md)을 따른다.

최종 글꼴, 표 헤더 배경·구분선·정렬, 입력 오류의 세부 장식, 페이지 구조와 다크 테마 등은 unresolved로 구분한다. 대표 화면의 임시값을 확정으로 승격하지 않으며 별도의 세부 질문을 이어가지 않는다. 필요한 기능이 정해졌을 때만 검토한다.

데스크톱 전용이며 모바일 대응은 제외한다. 공식·예선의 같은 요소를 비교하되 근거가 없는 값은 추정하지 않는다. 새 미션의 에이전트·도구·완료 조건, 승인된 루브릭과 CI 원칙은 디자인 때문에 바꾸지 않는다.
