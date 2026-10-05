---
name: topic-rubric
description: Compare hackathon topic candidates before implementation using evidence, agent benefit, feasibility and topic-v1 gates; exclude implementation quality and official judge-score prediction.
---

# 주제 선정 루브릭

후보 주제의 선정·보류·축소·제외와 가장 먼저 확인할 근거를 판단한다. 도구 수·바이오 분야·예선 진출 사실을 가점으로 쓰지 않는다. 평가 요청은 구현 변경·실모델/GPU 호출·게시를 승인하지 않는다.

## 기준과 입력

- [선정 기준](../../../docs/evaluation/topic-selection.md): 등급 해석·반례·판정 절차의 원본.
- [topic-v1 JSON](../../../docs/evaluation/topic-rubric.json): 계산용 배점·최저 등급·관문·근거 상한.
- [채점표](../../../docs/evaluation/templates/topic-scorecard.json)와 [채점기](../../../scripts/score.py).
- 선정 배경이 필요할 때만 [예선 분석](../../../docs/evaluation/topic-analysis.md)을 읽는다.

이 스킬은 저장소의 위 파일에 의존한다. 다른 프로젝트를 평가할 때에도 평가 대상의 자료를 쓰고, 스킬을 복사할 경우 의존 파일을 함께 준비한다. Claude 진입에서도 상대 경로는 이 본체를 기준으로 해석한다.

## 평가

1. 후보명(subject), 범위 버전(revision), 팀·시간·실행 조건(environment), 평가 시각(assessed_at)을 식별한다. context에 미션·사용자/실패·산출물·단순 기준선·관측별 행동·자료/권한·검증법·NVIDIA 역할·최소 범위를 기록한다. 확인하지 못한 사실은 명시하고 추정으로 채우지 않는다. 식별 정보가 없으면 숫자 대신 필요한 입력을 보고한다.
2. 기술명을 가린 상태에서 문제·에이전트 이득·검증 가능성을 먼저 본다. 자료의 존재와 접근 성공, 분기 존재와 규칙 대비 이득, 과거 성공과 현재 실행 가능성을 구분한다. 실제 모델의 자율성을 고정 규칙의 동작으로 대체하지 않는다.
3. 각 항목은 0~4 또는 null, evidence_level(claim/design/observed/compared), 근거 목록, note의 기대→관측→판정을 기록한다. 수준별 상한은 1/2/3/4이며 상한이 자동 점수는 아니다. 3·4는 항목별 조건까지 충족해야 한다. 합성 채점 예제를 실제 사용자 효용이나 live 관측으로 올리지 않는다.
4. 모든 관문에 pass/fail/unknown과 이유를 기록한다. pass/fail은 실제 근거가 필요하고 unknown은 다음 확인을 적는다. 높은 총점으로 실패 관문을 덮지 않는다. 본선 조건만 unknown이면 잠정 비교는 가능하지만 최종 선정은 보류한다.
5. 후보마다 채점표를 채우고 저장소 루트에서 `python3 scripts/score.py <채점표.json>`을 실행한다. 임시 입력은 /tmp에 둘 수 있고 보고서 저장은 요청 시에만 한다. 채점기는 형식·산술만 검증하며 근거의 진위·등급 적절성은 평가자가 확인한다.
6. 점수/100·미평가 배점·가능 범위, 항목별 근거·관문, 판정과 next_check를 보고한다. candidate는 선정 후보, hold는 보류, revise는 축소/재설계, exclude는 미션 부적합 제외다. provisional_candidate는 미션 확인 전 잠정 후보이며 확정 선정이 아니다. 5점 이내는 동률로 보고 결정적 불확실성을 먼저 확인한다.

후보 여러 개는 같은 미션·팀·시간 조건에서 비교한다. 실패 관문이 있는 후보와 근거가 부족한 후보를 구별하고, 변경된 범위는 새 버전으로 재평가한다. 최종 답에는 가장 먼저 할 확인 1개를 제시한다. 이 점수는 구현 품질·서비스 준비 완료·공식 심사 점수와 합산하거나 변환하지 않는다.
