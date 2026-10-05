# 공통 통합 — integration-v2

점수를 주지 않는 공동 관문이다. 에이전트/프런트의 같은 subject·revision·environment 평가가 있어야 한다. 담당별 점수를 평균해 통합 실패를 덮지 않는다. [숫자·관문 원본](integration.json)과 [양식](templates/integration-scorecard.json)을 쓴다.

| 관문 | 관측할 증거 | 책임 경계 |
|---|---|---|
| contract | 요청/응답 schema, run_id·후보 ID·seq, 오류·artifact 대응, 낡은/중복/역순 이벤트 처리 | agent는 정확한 payload, frontend는 표시, 통합은 전달의 일치 확인 |
| live_path | 실제 입력→NVIDIA 모델 선택/도구→검증→화면 결과의 같은 실행 기록 | HTTP 200·저장된 화면·합성 도구만으로 pass 불가 |
| failure_e2e | 실제 서비스 경계 오류 주입, bounded 종료/보류·부분 근거·재시작 | 각 영역 단위 테스트를 넘어 연결된 실패 확인 |
| reproducibility | 로컬 실행 명령·의존/설정 버전·입력/결과, 모드 표시, 비밀값 제외 | 새 배포나 팀원 장비 설치를 선행조건으로 추가하지 않음 |
| event_rules | 제공된 공식 미션·필수 기술·제출 요구의 준수 | 미제공은 unknown; 발표 점수·새 조사 과제 없음 |

agent는 결과의 정확성, frontend는 그 결과/한계의 표시, 통합은 두 값이 같은지 본다. 동일 실패를 세 번 가중 감점하지 않는다. 각각의 역할에서 실제로 확인한 별개 결함은 각 영역에 기록하고 통합 관문은 실패 전파를 확인한다.

두 영역 점수표가 영역 완료여도 관문 fail/unknown 하나면 product_ready=false다. 통합의 assessment_mode가 live가 아니어도 false다. 평가 모드만 live라고 쓰는 것으로 증거가 생기지 않는다. 원본 trace·화면·입력/출력의 대응을 사람이 확인해야 한다. 파일 경로만으로 실시간 연결·과학적 타당성을 보증하지 않는다.
