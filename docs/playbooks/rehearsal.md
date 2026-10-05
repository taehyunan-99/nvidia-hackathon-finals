# 로컬 실행 흐름 리허설

목적: 조합 검색 후 프런트와 에이전트 담당이 [같은 입출력 계약](../catalog/contracts.md)으로 연결하고, 관측 변화에 따른 도구 선택·검증·보류를 화면에서 확인한다. 배포나 API 키 없이 Python 표준 라이브러리와 브라우저로 실행한다.

## 검색 → 계약 → 화면

```sh
python3 scripts/lookup.py '조사 비교' --kind recipe --limit 1
python3 scripts/lookup.py '도구 선택' --kind agent --limit 3
python3 scripts/lookup.py 'nat-tools-and-functions' --kind skill --function build --limit 1
python3 scripts/lookup.py '입출력' --kind recipe --limit 1
python3 scripts/rehearsal.py --case supplement
python3 scripts/serve_preview.py
```

마지막 명령은 저장소 루트에서 실행하며 [로컬 화면](http://127.0.0.1:8765/design/agent-flow.html)을 연다. 프런트는 [fixture](examples/research/fixtures.json)를 즉시 소비한다. fixture를 수정하는 대신 runner를 변경한 뒤 `python3 scripts/rehearsal.py --write-fixtures`로 명시적으로 다시 생성한다. 출력 JSON은 사용 예시이며 별도 실행 이력 파일을 만들지 않는다.

## 확인할 동작

| 입력 case | 관측에 따른 경로 | 기대 결과 |
|---|---|---|
| existing | 기존 두 근거 확인 → 추가 조사 생략 → 검증 | completed |
| supplement | 기존 한 근거 → 추가 수집 → 검증 | completed |
| hold | 추가 수집해도 한 근거만 존재 | partial·기존 근거 유지 |
| failure | 추가 수집 timeout → 한 번 재시도 → 실패 | failed·확정 산출물 없음 |
| retry | 첫 timeout → 재시도 성공 → 검증 | completed·중복 근거 없음 |
| conflict | 두 근거가 상반된 값 | partial·상충 근거 유지 |

예선에서 재사용한 것은 기존 근거 활용·추가 도구 선택·부족한 근거 보류라는 흐름이다. HER2 도메인·실험 결과·예선 API 자체를 재현한 것이 아니다. `mock_decide`는 관측으로 분기하는 **규칙 기반 테스트 대역**이며 실제 LLM 자율 판단을 증명하지 않는다. live 연결에서는 이 경계에 모델의 선택을 넣고 허용 도구·인자·결과 검증기를 유지한다.

## 검사와 평가

`python3 -m unittest discover -s scripts -p 'test_*.py'`로 검색 경로·분기·조기 완료 거부·허용 도구·상한·잘못된 반환·fixture 일치를 확인한다. `python3 scripts/validate.py`로 링크·카탈로그·both 문서를 검사한다. 브라우저에서 6개 case, 단계별 근거, 중간 case 변경, 다시 시작, 키보드와 긴 문구를 확인한다. 검사는 실제 변경 영향에 따라 선택하며 API/GPU 검사는 포함되지 않는다.

[agent-rubric](../../.agents/skills/agent-rubric/SKILL.md)으로 평가할 때 대상은 현재 파일 버전과 `mock` 범위다. 실행하지 않은 live 판단·NVIDIA 기여·공식 미션/제출 조건을 성공으로 채점하지 않는다. 평가 결과는 대화로 전달하며 별도 완료·검증 이력 보고서를 만들지 않는다.

실제 구현 전환에는 도구 인자 schema·권한/모델·실제 오류/시간 제한·독립 검증·현재 입력의 live trace 확인이 남아 있다. 단순 Python 함수의 합성 timeout 테스트는 실제 네트워크 요청 중단을 검증하지 않는다.

## 한정된 실모델 연결 점검

`python3 scripts/probe_research.py`는 키 값 없이 설정 유무만 확인하는 dry-run이다. Git에서 제외된 로컬 `.env` 또는 프로세스 환경의 `NVIDIA_API_KEY`, `MODEL_ID`, `MODEL_BASE_URL`을 읽으며 셸 명령으로 실행하지 않는다. 실제 호출을 허용한 범위에서만 `python3 scripts/probe_research.py --live --output runs/research-live.json`을 사용한다. 실행 시작 시 기존 출력은 덮어쓰지 않는다. 한 실행 안에서는 완료된 case를 순서대로 저장하므로 출력에 두 case가 모두 있는지 확인해야 한다. 파일 존재나 최종 completed만으로 통과 판정하지 않고 기대 상태와 도구 경로를 함께 검사한다.

실행은 hosted NIM 모델 1개·합성 로컬 도구 2개이며 각 case에 최대 40회 요청·1,024토큰·10단계·900초, 일일 4,000회를 기본으로 둔다. 실행 간 요청 간격과 재시도까지 포함한 일일 누적은 [모델 호출 운영 기준](model-policy.md)을 따른다. API 키를 NVIDIA hosted endpoint 외에는 보내지 않는다. 이 도구는 NAT·실제 검색·실모델 반복 품질 시험을 대신하지 않는다.

로컬 화면에 `?source=live`를 붙이면 위 경로의 실행 데이터를 읽는다. 화면은 **실모델 실행 기록의 재생**이며 화면 조작으로 API를 추가 호출하지 않는다. LIVE 모델과 합성 도구를 함께 표시한다. `serve_preview.py`는 `.env`와 숨김 경로·디렉터리 목록을 제공하지 않고 필요한 디자인 assets만 예외로 제공한다.
