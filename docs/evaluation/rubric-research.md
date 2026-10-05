# 분리 루브릭의 조사 근거와 설계

확인일 2026-10-05. 아래 자료는 평가 방법의 근거이며 대회 공식 배점을 제공하지 않는다. 배점·80점 목표·최저 3등급·반복 3회는 이 팀의 제한된 로컬 시연을 위한 설계 선택이다. 효과는 본선 사례와 평가자 교정으로 계속 확인해야 한다.

## 외부 근거 → 적용

| 출처 | 채택한 원칙 | 적용 | 해석 한계 |
|---|---|---|---|
| [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 결과 상태와 실행 경로를 따로 관찰하고 코드·모델·사람 검사를 목적별로 조합; 반복 시도와 평가셋 관리 | agent goal/agency/correctness/reliability, 독립 검산·반례·기준선 | 자체 보고와 한 번의 완주가 업무 정답을 증명하지 않음; LLM 심사는 보조 |
| [NVIDIA NAT 평가 안내](https://raw.githubusercontent.com/NVIDIA/NeMo-Agent-Toolkit/develop/docs/source/improve-workflows/evaluate.md) | 도구 trajectory 평가와 결과 evaluator를 구분 | 실행 경로와 산출물의 증거 분리 | 공식 저장소 develop 문서를 확인; 방법론만 채택하며 현재 로컬 설치/API 지원은 별도 검증 |
| [Nielsen Norman Group: 10 Usability Heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | 상태 가시성·일관성·오류 예방/복구·핵심 정보 우선 | frontend task_flow/state_truth/recovery_ui/design | 휴리스틱 점검은 실제 사용자 과업 관측을 대체하지 않음 |
| [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | 키보드·초점·명암·색 외 단서의 검사 가능한 요구 | frontend accessibility | 일부 데스크톱 항목만 선정; 전체 WCAG 인증 아님 |
| [W3C 4.1.3 상태 메시지](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) | 초점을 이동하지 않아도 상태를 보조기술이 인식 | role/status 및 수동 보조기술 확인 | DOM에 role만 있다는 것으로 실제 발표/읽기 동작을 확인했다고 하지 않음 |
| [W3C 2.3.3 상호작용 애니메이션](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | 불필요한 상호작용 모션을 줄일 수 있어야 함 | reduced-motion 확인 | AAA 기준을 프로젝트 선택으로 채택; AA 필수라고 오기하지 않음 |

## 예선에서 얻은 반례

예선 revision `52f6be29e432b1fa660e2a9b3b6b7556d04793d4`의 [구현 근거](bio3-review.md)과 로컬 `docs/topics/her2/agent-benchmark-report.md`, `agent-improvement-review.md`, `frontend/src/AgentActivity.tsx`를 참고했다. 아래는 과거 기록 해석이며 이번에 예선 모델을 재실행한 결과가 아니다.

- 서비스 규칙 포함 최종 상태 8/8과 모델의 자율 선택·새 항체 정확도는 별개였다. 따라서 agency와 correctness를 분리하고 기준선 비교를 최고 등급에 둔다.
- 6/6 완주 개선과 신규 항체 접촉 F1=0 사례가 공존했다. reliability가 correctness의 점수를 대신할 수 없다. 캐시 재사용을 독립 표본으로 늘리지 않는다.
- 후보별 링·모델/규칙 주체·보류 표시에는 데이터 의미가 있다. frontend는 장식 개수보다 데이터→표현 규칙과 실제 사용자의 이해를 본다. 현재 합의한 순차 처리·공유 경로·복귀 모션 제거를 존중한다.

## 배점과 소유권

agent는 과업·선택·정확성에 60점을 둔다. 실행 제어 25점, NVIDIA의 실질 기여 10점, 신뢰 경계 5점을 더한다. frontend는 과업·상태·근거 이해에 55점, 회복 15점, 규칙 있는 시각 완성도 15점, 접근성 10점, UI 반응 5점을 둔다. 공급자 지연은 agent, 화면 반응은 frontend다.

공통 통합은 점수를 없애 중복 합산을 막았다. 발표는 평가에서 제거했고 팀원·GitHub 장식이나 3D의 존재는 독립 가점이 아니다. 새 UI 스택·도구 수·다중 에이전트를 강제하지 않는다.

## 유효성 검증 방식

채점기의 계산·unknown·등급 상한·교차 버전·중복 항목·대상 불일치·통합 관문을 반례로 검사한다. 두 스킬에는 서로 다른 영역만 평가하는 경계를 둔다. 정적 구현을 live 품질로 높이거나 예쁜 mock을 제품 준비 완료로 만드는 사례를 거부해야 한다. 이 검증은 루브릭의 논리·운영 안전성을 확인하며 심사 점수 예측력이나 팀원 간 일치도를 입증하지 않는다.
