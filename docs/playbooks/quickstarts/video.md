# 영상 미션 첫 실행

## VSS

1. `vss-deploy-profile`을 확보하고 필요한 기능에 맞는 profile과 GPU/메모리/서비스 의존성을 확인한다. [고정 스킬](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/vss-deploy-profile/SKILL.md).
2. 해당 profile 원문의 배포 명령으로 시작한다. 이미 서버가 있으면 주소/health와 실제 노출 tool 목록부터 확인한다.
3. `vss-ask-video`는 `video_understanding` 도구를 제공하는 profile이 필요하다. 서버 `/docs`를 확인하고 20초의 허용된 영상으로 새 시각 질문을 보낸다.
4. 기존 메타데이터/검색 결과로 답할 수 있으면 `vss-search-archive`, 영상 전체 요약은 `vss-summarize-video`를 선택한다. 출처 tool 결과를 재사용할지 새로 볼지 구분한다.
5. 답의 시간 구간과 프레임을 원본으로 검산한다. metadata 파일명을 읽은 결과는 시각 검증이 아니다.

## 실시간이면 DeepStream

`deepstream-dev`에서 host/GPU/Jetson·SDK 버전을 확인하고 `deepstream-generate-pipeline`으로 입력→decode→추론→결과 pipeline을 정한다. 테스트 stream 1개와 실제 모델 포맷을 먼저 검증한다. 기존 영상 서비스가 없다면 VSS/DeepStream 전체를 동시에 설치하지 않는다.

## 최소 완료와 축소

성공은 사건/물체의 답변과 원본 시각 근거가 연결되는 것. 미검출·접근 실패·빈 clip을 별도로 다룬다. 설치가 지연되면 live stream 대신 녹화 clip 한 개와 직접 VLM tool 경로를 검토한다. 사용 endpoint가 영상/프레임 입력을 실제 지원하는지 먼저 확인한다.
확인 수준: 공식 스킬 조사. profile 배포/영상 모델 실행은 미검증.
