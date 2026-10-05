# 음성 미션 첫 실행

`nemotron-speech`는 이전 Riva/NIM 명칭과 연결되는 문서 router다. [고정 원문](https://github.com/NVIDIA/skills/blob/0e0d506f4eb67204a62586ac5f19df3cb7ad9b1f/skills/nemotron-speech/SKILL.md).

1. ASR/TTS/번역 중 필요한 기능과 한국어 지원·모델·hosted/self-host를 고른다.
2. 스킬 `references/model-selection.md`와 선택 기능의 `asr.md`/`tts.md`/`nmt.md`를 읽는다. gRPC/HTTP/WebSocket 경로를 섞지 않는다.
3. 키·function/model ID·오디오 sample rate/encoding을 원문 예제와 맞춘다. hosted 예제를 사용하면 GPU 로컬 설치를 추가하지 않는다.
4. 짧은 공개/허용 발화 하나로 호출하고 실제 전사/출력 음성을 확인한다.
5. 전사를 NAT 도구 선택으로 넘기고 업무 결과를 별도 검증한다. `nemotron-voice-agent-builder`는 이 전체 흐름을 설계할 때 선택한다.

성공 확인: 알려진 문장과 전사 대조, 잘못된 발화·무음/잡음 처리, 도구 결과 확인. 실패 시 텍스트 입력으로 같은 업무 경로를 제공한다.
원문별 client 설치·호출 명령은 model/transport 결정 후 그대로 사용한다. 공통 URL 하나로 모든 음성 모델을 호출할 수 있다고 가정하지 않는다.
확인 수준: 조사. 마이크·한국어 실측·hosted 호출 미검증.
