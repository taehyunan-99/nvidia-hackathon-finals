# Brev GPU 크레딧 — 대회 당일 사용 가이드

확인일: 2026-10-06, 한국 시간. 2026-10-07 대회 준비용 사용법이다. 행사 명칭·일정·지급 조건의 원본은 [행사 안내](../operations/event.md)를 따른다.

**먼저 결론:** 필요한 모델과 기능을 NVIDIA 또는 다른 업체의 hosted API가 제공한다면 Brev 없이 에이전트를 만들 수 있다. Brev는 직접 모델·GPU 도구를 실행할 서버가 필요할 때 선택한다. 크레딧이 있다는 사실만으로 GPU를 켤 필요는 없다.

**2026-10-07 추가 요구:** OpenShell이 필수이며 외부 사용자가 직접 접속해 테스트해야 한다. 이제 Brev는 GPU 추론뿐 아니라 OpenShell·웹서비스 실행 호스트로도 검토한다. hosted API를 쓰더라도 sandbox를 운영할 환경은 필요하며, [Brev/별도 서버 비교와 배포 준비](openshell-deployment.md)를 따른다.

Brev에 OpenShell을 올리는 구체적인 host 접속·설치·생성·허용/차단·결과 회수는 [Brev OpenShell 설정 가이드](brev-openshell-setup.md)를 사용한다.

이 문서는 공식 사용법 조사와 팀의 선택 제안을 구분한다. 최초 작성 이후 2026-10-07 이 대화에서 계정 로그인·쿠폰 등록 후 $500 잔액·조직 초대 링크 생성을 확인했다. GPU 임대·모델 다운로드·추론·OpenShell 설치는 미수행이다. 명령은 실행 안내이며 검증 완료 기록이 아니다.

## 1. 당일 가장 먼저 확인할 것

- [ ] 주최 측이 지정한 계정·조직과 실제 크레딧 잔액 확인.
- [ ] 지급 코드, 만료일, 허용 GPU·개수, 개인 결제 필요 여부 확인.
- [ ] 외부 API·사전 코드 사용 및 NVIDIA 기술 관련 행사 조건 확인.
- [ ] 미션에 GPU 직접 운영이 필요한 이유를 한 문장으로 설명.
- [ ] 사용할 입력 1건, 기대 결과, 최대 사용 시간, 종료 담당 정하기.

과거 안내의 **L40S 1대·최대 $1,000은 현재 계정의 보장된 자원이 아니다.** 최신 PDF p.13은 팀당 약 $500·L40S 권장·팀별 자유 선택을 안내하며 실제 $500 등록도 확인했다. 만료일·인스턴스 가용량·요금은 [최신 미션](../operations/mission.md)과 콘솔을 대조한다. 이 문서가 지출 허가를 대신하지 않는다.

## 2. NVIDIA API, Brev, 모델 서버의 차이

| 구분 | 제공받는 것 | 우리가 준비하는 것 |
|---|---|---|
| NVIDIA hosted 모델 API | NVIDIA가 운영하는 모델의 응답 | 모델별 endpoint·권한·요청 형식·호출 한도 확인 |
| 다른 업체의 모델 API | 해당 업체가 운영하는 모델의 응답 | 별도 계정·키·요금·행사 허용 여부 확인 |
| Brev GPU 인스턴스 | GPU가 연결된 원격 실행 환경 | 코드·모델 설치, 실행, 서비스 연결, 백업·종료 |
| 직접 배포한 NIM·모델 서버 | 우리가 실행한 추론 서비스 | 지원 GPU·이미지·라이선스·인증·요청 형식 확인 |

API 방식도 공급자 서버의 GPU를 사용할 수 있다. 질문은 **“GPU 연산이 필요한가?”뿐 아니라 “그 GPU를 우리가 직접 운영해야 하는가?”**다. Brev는 에이전트의 계획·도구 선택·결과 검증을 자동 구현해 주지 않는다.

Brev 크레딧은 Brev 자원 비용의 잔액이다. 다른 업체 API 요금이나 NVIDIA hosted API 호출 한도가 같은 잔액에서 해결된다고 가정하지 않는다. 모델 API 키와 Brev CLI 인증도 서로 다른 용도다. [Brev 개요](https://docs.nvidia.com/brev/getting-started/overview), [CLI 인증](https://docs.nvidia.com/brev/cli/getting-started)

## 3. 언제 사용하는가 — 구체적인 선택 예시

아래는 팀의 설계 예시다. GPU가 항상 필수라거나 Brev가 항상 더 저렴하다는 뜻은 아니다.

| 상황 | 예시 | 먼저 선택할 경로 | Brev를 검토할 구체적 조건 |
|---|---|---|---|
| 일반 에이전트·RAG | 문서 검색 → 근거 비교 → 답변 | hosted LLM·임베딩 API + 로컬 서비스 | 필요한 모델·옵션을 API가 지원하지 않거나 자체 가중치가 필요 |
| 문서 OCR | 스캔 PDF의 표·수식 추출 후 누락 영역 재검사 | 사용 가능한 OCR API로 작은 입력 검증 | 직접 수정한 OCR 모델·전처리와 대량 배치를 같은 환경에서 실행해야 함 |
| 영상 분석 | 짧은 현장 영상에서 특정 부품을 분리·추적하고 의심 구간 재검사 | 영상·분할 API의 입력 길이·출력 확인 | 필요한 중간 마스크·특징값 접근, 추적 상태 유지, 사용자 코드 결합을 API가 제공하지 않음 |
| 파인튜닝 | 허용된 자체 데이터로 결함 분류기 또는 LoRA 학습 | 먼저 기존 모델의 실패 사례 확인 | 학습 데이터·평가셋이 준비됐고 개선할 문제가 분명하며 학습·평가 시간이 확보됨 |
| 자체 가중치 추론 | 팀이 학습한 체크포인트로 이미지 분류 | 해당 가중치를 수용하는 배포 서비스 확인 | 보유 가중치를 기존 API가 로드하지 못하고 직접 실행 코드가 있음 |
| GPU 전용 계산 | 사용자 CUDA 코드나 GPU 시뮬레이션을 도구로 호출 | 작은 입력은 CPU 가능 여부부터 확인 | 실행 라이브러리가 GPU를 요구하거나 실측상 CPU가 시간 예산을 넘음 |

### 예시 A: 외부 API로 충분한 문서 검토 에이전트

사용자 질문 → 로컬 에이전트가 문서 검색 → NVIDIA hosted LLM이 근거 비교 → 결과 검증 → 화면 출력.

이 흐름의 필요한 기능·한도를 API가 충족하면 Brev를 쓰지 않는다. 단순 API 호출, 화면 개발, 작은 CSV 집계, 일반적인 문서 검색 자체가 GPU 서버 임대 이유는 아니다.

### 예시 B: 직접 수정한 영상 분석 도구

사용자가 짧은 영상을 제출 → LLM이 검사할 물체·구간 선택 → Brev의 분할·추적 코드가 마스크와 시간별 결과 반환 → LLM이 누락된 구간을 골라 재검사 → 근거 화면과 결과 출력.

여기서 Brev를 쓰는 이유는 **중간 결과와 반복 처리 방식을 우리가 제어해야 하기 때문**이다. 외부 API가 같은 기능을 제공하면 API와 설치 시간·요금·지연을 비교한다. 분할 결과만으로 결함 판정이 완성되는 것은 아니며 별도 판정 기준이 필요하다.

### 예시 C: 자체 학습 모델

기존 모델이 특정 결함을 반복해서 놓침 → 허용된 라벨 데이터로 작은 학습 → 학습에 쓰지 않은 평가셋으로 비교 → 개선이 확인된 체크포인트를 에이전트의 도구로 연결.

이 경우 GPU는 학습·추론에 쓸 수 있다. 다만 대회 당일 데이터 수집·라벨링부터 시작해야 한다면 팀 제안은 파인튜닝보다 기존 모델과 도구 조합을 우선하는 것이다. 기존 hosted API에 프롬프트를 보내는 것만으로 우리 가중치가 학습·적용되지는 않는다.

### 예시 D: 많은 입력을 같은 모델로 반복 처리

예를 들어 허용된 영상 프레임 1,000장을 같은 모델로 처리할 때, 모델을 GPU 메모리에 올려 배치 처리하는 구성을 검토할 수 있다. 그러나 API에도 배치 기능이 있을 수 있고 업로드·설치 시간이 더 클 수 있으므로 작은 샘플로 총시간·비용을 측정한다. 이 저장소에서는 대량 처리 시 스크립트 작성 → 실행 → 결과 파일 저장 → 대화에는 요약만 읽는 순서를 따른다.

## 4. “GPU 서버에서만 가능한 모델”에 대한 오해

| 모델 | 확인한 사실 | 선택할 때의 의미 |
|---|---|---|
| [SAM 3 / 3.1](https://github.com/facebookresearch/sam3) | 이미지·영상 분할·추적 코드와 가중치 제공; [fal의 SAM 3 API](https://fal.ai/models/fal-ai/sam-3/image/api)도 존재 | SAM 3 사용 자체가 Brev 필수 근거는 아님. 버전·출력·수정 가능 범위를 비교 |
| [GLM-OCR](https://github.com/zai-org/GLM-OCR) | 자체 배포와 개발사 API 경로 모두 제공 | OCR에 GPU가 쓰인다고 우리 GPU 서버가 필요한 것은 아님 |
| [Depth Anything 3](https://github.com/ByteDance-Seed/Depth-Anything-3) | 깊이·카메라 자세 추정용 공개 실행 코드 제공 | 공간 분석 도구 후보이며 외부 API의 부재를 증명한 모델은 아님 |
| [SAM 3D Objects](https://github.com/facebookresearch/sam-3d-objects) | 사진에서 3D 형상·텍스처·배치 복원; 공식 [설치 조건](https://github.com/facebookresearch/sam-3d-objects/blob/main/doc/setup.md)은 Linux·NVIDIA GPU VRAM 32GB 이상 | 가중치 접근 승인·설치 난도를 먼저 확인. 생성된 형상을 정밀 실측값으로 취급하지 않음 |

**이번 조사에서는 “다른 업체 API도 전혀 없어서 GPU를 직접 운영해야만 하는 모델”을 확인하지 못했다.** NVIDIA의 API 키만으로 접근할 수 없는 것과, 모든 API 대안이 없는 것은 다르다.

NVIDIA 목록의 `Downloadable` 표시도 API 부재의 증거가 아니다. [Nemotron Parse 2.0](https://build.nvidia.com/nvidia/nemotron-parse-2.0)·[Parakeet](https://build.nvidia.com/nvidia/parakeet-tdt-0_6b) 상세 화면에는 무료 API 안내가 있다. 실제 제공 여부·권한은 당일 모델 페이지와 작은 요청으로 확인한다.

## 5. GPU를 켜기 전에 결정할 것

1. **모델·도구:** 정확한 모델 ID·revision 또는 컨테이너 tag, 가중치 접근 승인, 라이선스.
2. **자원:** GPU 종류·개수·VRAM, CPU RAM, 모델·데이터·결과를 담을 디스크, Stop 지원.
3. **한 건 검증:** 입력 1개, 기대 출력 형식, 최대 처리 시간, 실패 시 API·작은 모델·기능 축소 경로.
4. **비용:** 콘솔 실제 요금, 팀 총사용량, 만료일, 최대 실행 시간, 종료 담당.
5. **연결:** 로컬 서비스와 원격 모델의 주소·실제 포트·인증·timeout.

VRAM과 디스크는 다르다. 가중치 다운로드가 된다고 GPU 메모리에 들어가는 것은 아니다. 예를 들어 7B 모델의 FP16 가중치만 단순 계산하면 약 14GB이며, 실행에는 캐시·활성값 등의 추가 메모리가 필요하다. 학습·긴 입력·큰 배치는 요구량을 늘린다. 공식 모델 요구사항과 실제 할당 메모리를 확인하고, “L40S면 모든 모델 실행 가능”처럼 단정하지 않는다. [GPU 선택 안내](https://docs.nvidia.com/brev/reference/gpu-types)

API 요청 제한 때문에 자체 서버로 바꾸더라도 초기 다운로드·설치 시간, 처리량, 메모리 오류를 해결해야 한다. 보안상 외부 API를 쓸 수 없다는 이유만으로 Brev가 자동으로 허용되는 것도 아니다. Brev도 원격 클라우드이므로 데이터·제공자 조건을 별도로 확인한다. 오프라인 행사 환경의 해결책도 아니다.

## 6. 크레딧 등록과 과금 확인 — 브라우저

1. [Brev 콘솔](https://brev.nvidia.com/)에 주최 측에 제출한 계정으로 로그인한다.
2. 초대받은 팀 조직을 선택한다. 크레딧은 조직이 공유한다.
3. `Billing → Credits`에서 코드를 받았다면 `Redeem`으로 등록하고 실제 잔액을 확인한다. 이미 지급됐다면 잔액을 확인한다.
4. 제공 크레딧만 쓸 계획이면 `Auto recharge`를 끈다. 카드 등록 요구·코드 오류는 주최 측에 확인한다.
5. 잔액과 별개인 시간당 자원 한도도 확인한다. 확대 문의는 `brev-support@nvidia.com`으로 가능하다.

코드·잔액이 없다면 지급 시점·대상 조직부터 확인한다. [공식 Billing·콘솔 안내](https://docs.nvidia.com/brev/guides/console-reference)

팀 예산 계산은 `사용 가능한 잔액 ÷ 실행 중인 자원의 시간당 총비용`을 출발점으로 삼는다. 예를 들어 $100에 총 $2/시간이라면 저장공간 등 추가비용을 제외하고 약 50시간이다. **이 숫자는 계산 예시이며 실제 가격·지급액이 아니다.** 설정·다운로드·대기 시간도 서버가 실행 중인 시간에 포함해 계획한다.

## 7. 내 PC 준비 — GPU 생성 전에 수행

아래 예시는 인스턴스 이름을 `hackathon-gpu`로 사용한다. 다른 이름을 만들었다면 모든 명령에서 교체한다. 코드 블록은 해당 단계에서만 실행하고 전체를 한 번에 붙여넣지 않는다.

### 7.1 Windows: PowerShell에서 WSL 확인

```powershell
wsl --list --verbose
```

Ubuntu가 이미 있으면 그 환경을 사용한다. 없다면 관리자 PowerShell에서 설치하고, 재시작 후 Ubuntu를 열어 Linux 계정을 만든다.

```powershell
wsl --install -d Ubuntu-22.04
```

### 7.2 Windows의 Ubuntu 또는 Linux에서 CLI 설치

다음은 공식 설치 명령이다. 이 블록은 PowerShell이 아닌 Linux 셸에서 실행한다.

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/brevdev/brev-cli/main/bin/install-latest.sh)"
brev --version
brev login
```

### 7.3 macOS인 팀원의 경우

Homebrew가 설치된 로컬 터미널에서 실행한다.

```bash
brew install brevdev/homebrew-brev/brev
brev --version
brev login
```

브라우저가 열리지 않으면 `brev login --skip-browser`의 주소로 로그인한다. SSH 작업은 사용자 로그인을 사용한다. API key 로그인은 사용자 SSH 키를 설정하지 않으므로 동일한 접속 준비로 취급하지 않는다. [공식 CLI 설치·인증](https://docs.nvidia.com/brev/cli/getting-started)

## 8. 인스턴스 생성 — 브라우저

`GPUs → Create Instance`에서 크레딧 조직, 이름 `hackathon-gpu`, GPU 1개, 작업에 맞는 환경, 디스크를 선택한다. 주최 측 Launchable이 있으면 그 설정과 요구사항을 먼저 확인한다. 요금·Stop 지원을 확인하고 `Create`를 누른 뒤 `Running` 및 설정 완료를 기다린다. [공식 생성 절차](https://docs.nvidia.com/brev/guides/console-reference)

첫 실행의 팀 제안은 준비된 PyTorch 환경이나 목적에 맞는 Launchable이다. 모든 프레임워크·모델을 설치하지 말고 한 모델·입력 한 건부터 시작한다. CLI 생성 명령의 GPU 식별자를 과거 예시에서 복사해 고정하지 않는다.

## 9. 접속과 GPU 확인

### 9.1 내 PC의 Ubuntu/macOS/Linux 터미널

첫 명령의 실제 조직 이름으로 `YOUR_ORG_NAME`을 교체한다.

```bash
brev list orgs
brev set "YOUR_ORG_NAME"
brev refresh
brev list
brev shell hackathon-gpu
```

성공 기준: 의도한 조직의 인스턴스가 표시되고 원격 셸에 접속한다. 이때부터 해당 창은 GPU 서버 터미널이다. [조직·인스턴스 관리](https://docs.nvidia.com/brev/cli/instance-management)

### 9.2 원격 GPU 서버 터미널

```bash
cd /home/ubuntu/workspace
nvidia-smi
python3 --version
df -h .
```

GPU 이름·메모리 표가 나오면 장치 인식 성공이다. 기본 환경에서는 작업 파일을 `/home/ubuntu/workspace`에 둔다. 사용자 컨테이너는 마운트 경로를 별도 확인한다. [Quickstart](https://docs.nvidia.com/brev/getting-started/quickstart), [파일·컨테이너 경로](https://docs.nvidia.com/brev/guides/development-tools/file-transfer-scp)

PyTorch가 있는 환경에서 아래로 실제 GPU 연산까지 확인한다.

```bash
python3 - <<'PY'
import torch
assert torch.cuda.is_available(), "현재 Python 환경에서 CUDA를 사용할 수 없습니다."
x = torch.randn(1024, 1024, device="cuda")
y = x @ x
torch.cuda.synchronize()
print("GPU:", torch.cuda.get_device_name(0))
print("연산 성공:", y.shape, y.device)
PY
```

`연산 성공`과 `cuda:0`이 기준이다. `torch`가 없거나 CUDA가 False면 현재 Python 환경과 CUDA 지원 설치를 확인한다. 드라이버를 무작정 재설치하지 않는다. [공식 GPU·PyTorch 문제 해결](https://docs.nvidia.com/brev/troubleshooting/instances-gpus/gpu-detection-pytorch), [PyTorch 설치 선택기](https://pytorch.org/get-started/locally/)

Docker를 사용하는 작업이면 추가로 `docker version`, `docker info`와 선택한 이미지의 GPU 노출을 확인한다. 기본 접속 대상인 개발 컨테이너와 실제 host가 다를 수 있으므로 제품 지침에 따라 `brev shell hackathon-gpu --host`를 사용한다. [접속 대상 안내](https://docs.nvidia.com/brev/cli/connectivity)

## 10. 코드·모델 준비와 최소 추론

원격의 `/home/ubuntu/workspace` 아래에서 실제 저장소를 clone하고 README의 설치 순서를 따른다. 비공개 저장소 접근 인증과 모델 가중치 다운로드 권한은 별도로 필요할 수 있다. 키는 저장소·프런트엔드·로그에 넣지 않는다.

로컬에만 있는 파일은 **내 PC 터미널**에서 전송한다. `./my-project`는 실제 업로드 폴더로 교체하고 `.env`·키·캐시를 제외한 폴더를 준비한다.

```bash
brev copy -r ./my-project hackathon-gpu:/home/ubuntu/workspace/
```

Windows의 D 드라이브는 일반적인 WSL 설정에서 `/mnt/d/`로 접근한다. 이 저장소는 준비 문서 중심이므로 저장소를 복사하는 것만으로 모델 서비스가 시작되는 것은 아니다. [공식 파일 전송](https://docs.nvidia.com/brev/guides/development-tools/file-transfer-scp)

실제 추론은 선택한 모델 공식 예제의 입력 1개로 실행한다. 모델 ID·명령·포트는 모델이 정해진 뒤 그 문서에서 가져온다. 성공 여부를 다음 단계별로 구분한다.

| 확인 | 성공 근거 | 아직 보장하지 않는 것 |
|---|---|---|
| 접속 | 원격 셸 열림 | GPU 사용 가능 여부 |
| GPU 장치·연산 | 장치 표 + CUDA 연산 성공 | 모델 설치·추론 성공 |
| 모델 최소 추론 | 실제 입력에 유효한 결과 반환 | 에이전트 통합·품질 |
| 에이전트 통합 | 도구 호출 → 결과 확인 → 정상 종료 | 변화·오류 입력 대응 |
| 시연 준비 | 정상·입력 변화·실패 각각 확인 | 모든 입력에 대한 성능 보장 |

## 11. 개발 도구와 로컬 서비스 연결

### VS Code

로컬에 VS Code를 설치하고 **내 PC 터미널**에서 실행한다.

```bash
brev open hackathon-gpu
```

원격 프로젝트 폴더를 열어 작업한다. [공식 VS Code 안내](https://docs.nvidia.com/brev/guides/development-tools/vscode-setup)

### Jupyter가 필요한 경우

원격 GPU 서버에서 실행한다. Jupyter가 이미 실행 중이면 기존 주소·포트를 사용한다.

```bash
jupyter lab --no-browser --port=8888
```

내 PC의 새 터미널에서 포트를 연결하고 그 창을 유지한다.

```bash
brev port-forward hackathon-gpu --port 8888:8888
```

브라우저에서 `http://localhost:8888`을 열고 원격 실행 출력의 토큰으로 인증한다. 인증을 끄지 않는다. [공식 Jupyter 안내](https://docs.nvidia.com/brev/guides/development-tools/jupyter-notebooks)

### 에이전트의 GPU 도구 서버 연결

구성 예시: `로컬 UI → 로컬 에이전트 → 포트 전달 → Brev의 GPU 도구 → 결과 검증`.

**먼저 원격에서 모델·도구 서버를 실제로 실행해야 한다.** 아래 8000은 설명용 예시이며, 원격 서버가 실제 8000에서 준비된 경우에만 내 PC의 새 터미널에서 실행한다.

```bash
brev port-forward hackathon-gpu --port 8000:8000
```

같은 PC의 클라이언트에서 `http://localhost:8000`으로 연결하되, 실제 요청 경로·payload·인증은 선택한 서버 문서를 따른다. 모든 서버가 `/v1/chat/completions`를 지원한다고 가정하지 않는다. Windows 클라이언트에서 WSL의 전달 포트에 접근되지 않으면 먼저 같은 WSL에서 확인하고 로컬 네트워크 전달을 점검한다.

로컬 8000이 사용 중이면 `--port 18000:8000`으로 바꾸고 클라이언트 주소도 18000으로 맞춘다. 포트마다 별도 명령을 실행한다. 웹 Tunnel은 브라우저 인증이 개입할 수 있어 프로그램 연결에는 CLI 포트 전달을 우선한다. [공식 포트 전달](https://docs.nvidia.com/brev/cli/connectivity)

`localhost`는 각자 PC를 뜻한다. 팀원 PC에서도 사용할 경우 팀원이 자기 계정·조직 권한으로 로그인해 자체 포트 전달을 열어야 한다. Brev를 인터넷 전체에 공개 배포하지 않아도 로컬 시연은 가능하다.

에이전트에는 [공통 호출 정책](model-policy.md)의 재시도·요청 수·단계·시간 상한을 연결한다. Brev를 쓴다고 무한 재시도나 무제한 GPU 병렬 실행을 허용하지 않는다. 시각 모델 등 토큰 출력이 없는 도구에는 해당 출력 토큰 제한 대신 작업별 크기·시간·동시성 제한을 명시한다.

## 12. 백업 → 중지 → 재시작 또는 삭제

### 12.1 결과 백업 — 내 PC 터미널

아래 원격·로컬 폴더를 실제 결과 위치로 교체한다. 로컬 디스크 여유도 확인한다.

```bash
brev copy -r hackathon-gpu:/home/ubuntu/workspace/my-project/outputs ./brev-outputs
```

다운로드된 파일을 열어 확인한다. 코드 수정과 모델 설정·필요한 체크포인트도 보존한다. 코드의 Git 백업만으로 대용량 결과 파일까지 백업됐다고 가정하지 않는다. [결과 다운로드 안내](https://docs.nvidia.com/brev/guides/development-tools/file-transfer-scp)

### 12.2 잠시 중지

팀원이 사용 중인지 확인하고 내 PC 터미널에서 실행한다.

```bash
brev stop hackathon-gpu
brev list
```

콘솔에서 Stopped까지 확인한다. **터미널·브라우저 닫기, `exit`, Python 프로세스 종료는 인스턴스 중지가 아니다.** Running이면 연산하지 않아도 컴퓨팅 비용이 발생하며, Stopped에도 저장공간 비용이 남을 수 있다.

### 12.3 다시 사용

실제 기존 인스턴스 이름을 확인한 뒤 실행한다.

```bash
brev start hackathon-gpu
brev refresh
brev shell hackathon-gpu
```

GPU가 같은 공급자·지역에 없으면 재시작이 실패할 수 있다. 재시작 후 모델 프로세스와 포트 전달도 다시 확인한다. 발표 직전의 중지·재시작은 이 가용성 위험과 잔액을 함께 고려한다. [인스턴스 수명 주기](https://docs.nvidia.com/brev/concepts/gpu-instances)

### 12.4 완전히 종료

백업·팀원 사용 종료 확인 후 실행한다. **삭제한 인스턴스와 데이터는 복구할 수 없다.**

```bash
brev delete hackathon-gpu
brev list
```

콘솔에서도 남은 자원과 Billing 사용량을 확인한다. `--all` 같은 조직 전체 대상 명령은 이 안내의 기본 종료 방식으로 사용하지 않는다. [관리 명령](https://docs.nvidia.com/brev/cli/instance-management)

잔액 소진 시 중지 가능한 인스턴스는 일시 중지되고 불가능한 자원은 삭제될 수 있으며, 미충전이 지속되면 나머지 자원도 삭제될 수 있다. **잔액 0을 자동 종료·백업 전략으로 삼지 않는다.** [크레딧 소진 정책](https://docs.nvidia.com/brev/guides/console-reference)

## 13. 현장에서 막혔을 때

| 증상 | 첫 확인 | 복구·축소 경로 |
|---|---|---|
| 크레딧 0 / 코드 오류 | 로그인 계정·조직·코드 사용 여부 | 주최 측 확인, 개인 결제로 임의 대체하지 않기 |
| 잔액은 있지만 생성 실패 | GPU 재고·조직 자원 한도·행사 허용 GPU | 허용되는 작은 GPU 또는 hosted API 검토 |
| 인스턴스가 안 보임 | 조직·Running 상태 | `brev refresh` 후 목록 확인 |
| CLI 설치 중 GitHub 제한 | 공식 설치 문서의 GitHub rate limit 항목 | 허용된 다른 네트워크 또는 `gh auth login` 후 재시도; 토큰 출력 금지 |
| WSL SSH는 되는데 VS Code 실패 | Windows SSH와 WSL SSH 경로 차이 | 우선 `brev shell`; [공식 WSL 연결 해결](https://docs.nvidia.com/brev/troubleshooting/ide-connectivity/vscode-windows-wsl) 적용 |
| GPU는 보이나 CUDA False | 실행 중인 Python·PyTorch 설치 | [공식 진단](https://docs.nvidia.com/brev/troubleshooting/instances-gpus/gpu-detection-pytorch)에 따라 환경 확인 |
| CUDA out of memory | 모델 요구량·동시 작업·배치·해상도·입력 길이 | 불필요 프로세스 종료, 입력·배치 축소, 지원되는 작은 모델·양자화 검토 |
| 포트 접속 실패 | 원격 서비스가 실제로 실행되는지, 포트·로그 | 원격 한 건 확인 → 로컬 포트 전달 확인 → UI 연결 순서 |
| 팀원만 접속 실패 | 팀 권한·팀원 PC의 포트 전달 | 각자 인증·자기 localhost 사용 |
| API 요청이 로그인 HTML 반환 | 브라우저용 Tunnel 사용 여부 | CLI 포트 전달과 실제 API 경로 확인 |
| 재시작 불가 | 원 공급자·지역의 GPU 재고 | 중지 전 백업 사용, API·대체 환경으로 축소 |

팀 제안: 설치·접속 문제를 해결할 시간 예산을 미리 정한다. 핵심 작업 한 건이 그 예산 안에 실행되지 않으면 API·작은 모델·축소 기능으로 전환한다. 저장된 시연 결과를 사용할 때는 실시간 실행인 것처럼 표시하지 않는다.

## 14. 발표·시연 직전 체크

- [ ] 잔액·남은 시간·인스턴스 상태와 종료 담당 확인.
- [ ] 모델 준비 완료 후 실제 입력 1건을 실행하고 출력·지연 확인.
- [ ] 로컬 UI에서 GPU 도구까지 연결 확인. 서버와 포트 전달 창 유지.
- [ ] 정상·입력 변화·실패 입력을 확인하고 실패 시 명확히 중단·축소.
- [ ] 종료 후 코드·결과 백업, 인스턴스 중지 또는 삭제 확인.

설명할 핵심은 “GPU를 사용했다”가 아니라 **어떤 사용자 작업에 어떤 연산이 필요했고, 에이전트가 그 도구의 결과를 어떻게 검증했는가**다. Brev 사용 자체의 가산점·필수 여부는 공식 행사 조건으로 확인한다.

## 15. 자주 하는 질문

**NVIDIA API 키가 있는데 Brev도 써야 하나?** 필요한 hosted 모델·기능·한도가 충족되면 필요 없다. 직접 학습·자체 가중치·추론 코드 수정·GPU 전용 계산이 필요할 때 검토한다.

**SAM 3를 쓰면 GPU 서버가 꼭 필요한가?** 아니다. 다른 업체 API도 있다. 원하는 버전·중간 결과·영상 처리 방식이 API로 가능한지 먼저 비교한다.

**크레딧을 등록하면 GPU가 자동으로 생기나?** 잔액 확인과 인스턴스 생성은 별도 단계다. 생성·실행 상태와 사용량을 확인해야 한다.

**노트북에 NVIDIA GPU가 있어야 하나?** Brev GPU는 원격에 있다. 노트북은 접속·개발·화면을 담당할 수 있으며, 로컬 GPU 유무보다 인터넷·계정·접속 환경을 먼저 확인한다.

**Brev를 쓰면 모델 학습부터 해야 하나?** 아니다. 공개된 가중치의 추론만 실행할 수 있다. 파인튜닝은 검증할 필요가 있을 때 별도 작업으로 선택한다.

**두 명이 한 인스턴스를 써도 되나?** 조직 권한을 통해 접근하되 같은 GPU 메모리·파일·포트를 공유한다는 점을 고려한다. 한 명이 종료하면 다른 사람의 작업도 영향을 받을 수 있다.

관련 문서: [Brev 도구 카드](../catalog/tools/brev.md) · [GPU·격리 runtime 최소 안내](quickstarts/runtime.md) · [모델 호출 정책](model-policy.md) · [행사 조건](../operations/event.md).
