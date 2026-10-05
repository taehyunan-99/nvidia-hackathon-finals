# Bio-3 예선 구현 근거

2026-10-03 조사 기준: 예선 저장소 `52f6be29e432b1fa660e2a9b3b6b7556d04793d4`. 아래는 당시 코드·실행 기록의 관측 근거이며 현재 원격 서비스를 재실행한 결과가 아니다.

이 문서는 구현·시험 사실과 그 한계를 관리한다. 선정 경위·대회 적합성·장단점 해석은 [주제 분석](topic-analysis.md), 새 후보의 판단은 [선정 기준](topic-selection.md)을 따른다.

사용자 확인: 예선은 배포 서비스와 GitHub 중심으로 제출했다. 정확한 제출 commit·지원서 문구·심사위원 열람 경로·항목별 점수는 미확인이다. 2026-10-05 사용자는 심사 피드백이 없으며 주제가 가점인지 감점인지 알 수 없다고 확인했다.

## 구현에서 확인한 역할

| 위치 | 확인한 구현 | 해석 경계 |
|---|---|---|
| `logic/agent_session.py` | 상태별 허용 도구·중복 호출 제한, 재사용/예측/보류 선택 | 코드가 제한한 선택 공간이며 모든 단계를 LLM이 자유 계획하는 것은 아님 |
| `logic/nat_workflow.yml` | Nemotron과 NAT 도구 등록, 필요한 Boltz-2 예측 연결 | 스택 사용 사실과 예측 정확도는 별개 |
| `logic/runtime_skill.py` | 고정 스킬 지침·해시 검사 | 스킬 설치 자체를 실제 과업 완료로 세지 않음 |
| `logic/review_policy.py` | 항목별 근거·후보·조건 대응과 의견 연결 | 검토 의견은 결합력·치료 효능의 순위가 아님 |
| 서비스 화면·보고 | 기본 실험/예측 비교 입력, 3D·출처·보고·다운로드, model/rule 및 selected/skipped/failed/held 구분 | 심사위원이 실제 열람했는지는 미확인 |

## 실행 근거와 해석 한계

| 기록 | 관측 사실 | 해석 경계 |
|---|---|---|
| 초기 고정 평가 `7c5cf2d` | 13/20, 치명 항목 5개 | 과거 코드의 결함 기록; 현재 점수 아님 |
| 과거 모델 benchmark → 호출 복구 후 | 2/6 → 6/6 완주, 429 7회 복구 | 작은 회귀 시험. 후속 회차는 예측 캐시 사용, 새 정확도 검증 아님 |
| 최종 입력/예측 계약 검증 | 공개 구조+가상 변이 한 실행, 약 113.1초, 규칙 복구 0 | 한 입력의 end-to-end 성공 |
| WT+D185A 실제 공개 후보 | 브라우저 접수→NAT/Boltz→저장/결과, 약 128.7초, 규칙 복구 0 | 서열/좌표 대응 확인이며 결합력 검증 아님 |
| WT+D185A+Fab37 | 약 220.8초, 예측+실험 구조 선택+Fab37 계산 보류, 규칙 복구 0 | 구조가 있어도 계산 조건이 부족하면 보류하는 흐름 |
| 결과 연결·운영 검사 | 새로고침 후 동일 실행, JSON/CSV·구조 파일, 세션 격리·별도 볼륨 복원 기록 | 이번에 원격 E2E를 다시 실행한 것은 아님 |

두 실제 공개 후보 실행의 D185A 예측 파일은 같은 해시이므로 독립 정확도 표본으로 중복 집계하지 않는다. 기존 신규 항체 2건의 실험 접촉 대비 예측 F1=0이라는 반례도 유지한다. 코드/검증 기록의 완성도는 과학적 예측 정확도를 보장하지 않는다.


규칙 비교군도 같은 8개 입력의 최종 상태를 맞혔다. 모델의 결과 정확도 우위는 그 시험에서 확인되지 않았으며, 경로 선택·호출 비용·과학적 정확도를 최종 상태 일치와 구분한다.

## 과거 내부 평가

기존 73.75/100은 [finals-v1](legacy/rubric.md)의 자료 기반 주관적 시범 점수다. 실제 예선 점수·현재 구현 평가·주제 선정 점수로 변환하지 않는다. 당시 배점과 계산법은 [과거 채점 안내](legacy/scoring-guide-v1.md)에 보존하며, 현재 기준은 [평가 진입](README.md)을 따른다.

## 근거 원문

- [공식 행사](https://fastcampus.co.kr/NVIDIA_hackathon) · [예선 이미지](https://cdn.day1company.io/prod/uploads/202609/153942-1931/%E1%84%80%E1%85%A2%E1%84%8B%E1%85%AD-01.webp) · [본선 이미지](https://cdn.day1company.io/prod/uploads/202609/153945-1931/%E1%84%80%E1%85%A2%E1%84%8B%E1%85%AD-02.webp).
- [프로젝트 README](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/README.md) · [시나리오·실행 검증](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/docs/frontend-hosting/test-data.md) · [분석 검증 계약](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/docs/topics/her2/analysis-validation-contract.md).
- [실모델 benchmark](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/docs/topics/her2/agent-benchmark-report.md) · [후속 개선](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/docs/topics/her2/agent-improvement-review.md) · [의견 판정 코드](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/logic/review_policy.py).
