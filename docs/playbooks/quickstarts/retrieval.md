# 문서 검색·RAG 첫 실행

## 작은 검색 경로

원격 NIM/service를 쓰는 client와 GPU local ingest를 구분한다. 원문 스킬이 요구하는 endpoint/모델 설정을 먼저 읽고 공개/허용된 문서 3개를 `corpus/`에 준비한다.

```sh
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python "nemo-retriever==26.8.1"
.venv/bin/retriever --help
.venv/bin/retriever ingest corpus --lancedb-uri lancedb --table-name mission
.venv/bin/retriever query "What is the stated deadline?" --lancedb-uri lancedb --table-name mission --top-k 5 --format evidence
```

이 명령은 원격 client 경로의 시작이며 문서 유형별 추출 모델/키/서비스 설정 없이 모두 작동한다는 보장이 아니다. [고정 스킬](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemo-retriever/SKILL.md)의 remote/local/service 모드를 따른다. Windows에서는 `.venv/Scripts/` 경로를 사용한다.

## agent 연결

검색 함수를 `query→[{source_id,page,text}]` 형태로 감싼다. agent는 부족하면 재검색하거나 보류한다. 출처/페이지/수치 대조는 별도 validator가 수행한다. 답이 없는 질문에서는 검색 결과의 존재와 정답 근거의 존재를 구분한다.

## RAG Blueprint가 필요한 경우

이미 전체 서비스를 돌릴 환경이 있으면 `rag-blueprint`의 `references/deploy.md`에서 Docker/Helm/library 중 하나를 선택한다. 해당 서비스의 OpenAPI에서 ingest→query endpoint를 확인한다. 포트나 payload를 추측해 호출하지 않는다. [원문](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/rag-blueprint/SKILL.md).
`rag-eval`은 blueprint의 `corpus/`, `train.json`, 평가 runner 구조를 전제로 한다. 임의 프로젝트에 설치만 하고 같은 명령이 된다고 가정하지 않는다.

## 확인 / 실패

성공: 문서 위치까지 추적 가능한 검색 1건, 답 없음 1건, 잘못된 원문 인용 거부 1건. 인덱스 생성은 답변 정확도 검증이 아니다.
실패: 모델/ingest endpoint/문서 형식을 분리 점검하고 텍스트 문서 한 개부터 축소한다. 모델에 전체 PDF를 주고 '검색 완료'로 바꾸지 않는다.

확인 수준: 공식 명령 조사, 이번 환경의 Retriever/NIM 실실행 미검증.
