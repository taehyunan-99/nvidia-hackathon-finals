# BioNeMo 전문 미션 첫 실행

모델 선택: 단백질 복합체 구조는 Boltz-2, 분자 docking은 DiffDock, 분자 생성은 GenMol을 각각 검토한다. 이름이 비슷해도 입력/정답 기준이 다르다.

1. [전체 인덱스](../../catalog/skills-index.json)에서 실제 선언 이름(`boltz2-nim`, `diffdock-nim`, `genmol-nim`)과 고정 원문을 확인한다.
2. 해당 스킬의 `references/api.md`/validation 문서에서 모델별 hosted endpoint·request/response schema·키 이름을 확인한다.
3. 공개/허용된 작은 입력과 모델별 제한을 먼저 검증한 후 한 번만 실행한다. 동일 요청 hash의 결과는 구분 보관한다.
4. Boltz-2는 mmCIF/사슬/서열·좌표를 검사하고 모델 신뢰도와 실험 일치도를 분리한다. DiffDock/GenMol은 입력 분자/표적의 형식·유효성과 출력 검증 기준을 해당 모델 문서에서 확인한다.
5. 실제 자료가 부족하면 미확인을 표시한다. 항체 구조 신뢰도나 small-molecule affinity 지원을 항체 결합력/효능의 증거로 바꾸지 않는다.

예선에서 배울 점은 [주제 분석](../../evaluation/topic-analysis.md), 당시 실행 사실은 [구현 근거](../../evaluation/bio3-review.md)를 따른다. 예선의 HER2 입력 규격·도메인 기준을 새 미션에 자동 적용하지 않는다.
성공 확인: 파일을 만들었다는 사실 외에 입력 대응/출처/의도한 계산의 검산. API 실패는 과학적 실패와 별도 기록한다.
확인 수준: 공식 모델 스킬 조사. 본선 새 분자 예측/실험 검증 미실행.
