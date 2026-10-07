# OpenShell 보안정책과 샌드박스 분석

조사 기준: **2026-10-07, 한국 시간 / OpenShell v0.1.2**. 공식 문서·릴리스를 조사한 설계 자료다. 조사 이후 Brev 0.1.2의 합성 파일·반출·결과 회수 검증이 진행됐으며 현재 범위와 실제 근거는 [OpenShell 하네스](../../playbooks/openshell-harness.md)를 따른다. 제품 에이전트·모델/API 통합 성공을 뜻하지 않는다. 실행 환경 선택과 외부 접속 검증은 [배포 준비](../../playbooks/openshell-deployment.md)를 따른다.

후속 로컬 확인에서는 `openshell --version`이 `0.0.116`이었다. CLI 존재만으로 이 문서의 v0.1.2 설정이나 sandbox 실행이 검증된 것은 아니다. 현재 [가족 MVP](../../product/README.md)의 실제 연결 전 버전 정합성을 확인한다.

이후 제공된 슬랙·PDF·녹취·챌린지 저장소의 행사 요건은 [본선 미션 원본](../../operations/mission.md)을 우선한다. Brev 계정·크레딧 등록과 이후의 [모델 없는 연결 시험](../../playbooks/aws-brev-deployment.md), [합성 프런트 공개](../../playbooks/frontend-deployment.md)를 구분한다. 아래 `/workspace` 예시는 합성 설계 예시이며 공식 테스트는 `/hackathon/input`, `/hackathon/output`, `/hackathon/restricted`, `/hackathon/secrets`를 사용한다.

## 1. 이번 미션에서 확인된 범위

| 항목 | 현재 판단 | 근거와 처리 |
|---|---|---|
| 큰 주제 | 한국 문화·역사·지역·여행의 맥락·신뢰성 판단 | 슬랙·PDF 확인; 후속 사용자 결정은 한국 가족 문화체험 참여조건 확인 |
| 필수 도구 | NVIDIA OpenShell | 슬랙·PDF가 심사 자격 필수 요건으로 명시 |
| 보안정책 | 공통 테스트와 NVIDIA 기술 40점의 중요한 평가 대상 | 40점 전체가 파일 차단만의 점수라는 뜻은 아님 |
| 샌드박스 환경 | Brev 또는 별도 환경 | 별도 환경·CPU 선택은 구두 보충, 특정 클라우드나 GPU 의무로 해석하지 않음 |
| 사용자 테스트 | 사용자가 직접 접속해 테스트할 수 있어야 함 | 사용자 요구; 외부 접속 가능한 배포를 설계 범위에 포함 |
| 이 문서의 최초 조사 범위 | 조사·분석·문서화 | 이후 실제 연결·공개·보안 검증은 상단의 각 실행 문서에서 구분 |

**설계 결론:** 에이전트의 실제 도구 실행을 OpenShell 샌드박스 안에 두고, 허용된 문화 자료 접근과 금지된 접근의 차이를 실행 증거로 보여주는 구성이 적합하다. 외부 사용자는 웹서비스로 접근하고, 관리자는 별도 경로에서 정책과 실행 환경을 관리한다. 이 절은 범용 설계 근거이며 현재 제품의 목적·조합·실행 상태는 [제품 원본](../../product/README.md)을 따른다.

## 2. OpenShell이 담당하는 일

OpenShell은 에이전트를 실행하는 격리 환경과 권한 정책을 제공하는 런타임이다. 프롬프트에 지침을 넣는 것에 더해 파일·프로세스·통신의 실행 경계에서 권한을 적용한다. 모델 자체, 한국 문화 데이터, 웹서비스 UI, 사용자 인증을 모두 제공하는 완성 서비스는 아니다.

| 구성 | 역할 | 이번 서비스에서의 의미 |
|---|---|---|
| Gateway | 샌드박스 생명주기·정책·provider·인증과 관리 연결 | 서비스 백엔드와 운영자가 사용하는 관리 지점 |
| Compute runtime/driver | Docker·Podman·Kubernetes·MicroVM으로 실행 경계 생성 | 실제 배치 환경에 맞춰 하나를 선택 |
| Sandbox workload | 에이전트와 도구가 실행되는 비신뢰 영역 | 검색·파일 처리 등 정책을 검증할 실제 작업 위치 |
| Supervisor | 경계 바깥에서 정책 평가·DNS·허용된 통신·자격증명 대체 수행 | 에이전트가 자신의 허용 범위를 직접 바꾸지 못하도록 분리 |
| Provider/profile | 서비스 자격증명과 허용 endpoint·실행 파일 연결 | 모델 API 등의 진짜 키를 에이전트에 직접 전달하지 않는 경로 |
| Advisor/prover | 정책 제안·위험 검사·정의된 경계와의 비교 | 필요한 권한 확대를 검토하고 과도한 정책을 발견 |

workload의 외부 통신은 보호된 supervisor 연결을 거친다. v0.1.2 구조에서는 sandbox 내부 구성요소가 관측을 전달하고, 신뢰된 supervisor가 정책을 판단한다. 기존 글의 “샌드박스 내부 프록시가 모든 것을 처리한다”는 설명을 그대로 새 구조에 적용하지 않는다. [공식 구조](https://docs.nvidia.com/openshell/v0.1.2/about/architecture)

### 다른 도구와의 경계

| 도구 | 담당 | 대체하지 않는 것 |
|---|---|---|
| OpenShell | 실행 격리와 파일·통신·자격증명 정책 | 사실 검증, 서비스 업무 규칙, 사용자 인증 |
| Brev | 원격 컴퓨팅 환경·접속·환경 재현 | OpenShell 정책의 작성·차단 검증 |
| 에이전트/모델·NAT 등 | 목표 해석·도구 선택·작업 진행 | OS 수준 실행 격리 |
| 애플리케이션 검증기 | 입력·결과·업무 권한·호출 한도 검사 | 샌드박스의 시스템 접근 통제 |

OpenShell을 사용한다고 NemoClaw나 OpenClaw를 반드시 도입해야 하는 것은 아니다. 공식 실행 안내는 이미지 안에 있는 에이전트를 주 프로세스로 실행하는 방법을 제공한다. 우리 코드도 필요한 도구를 담은 이미지와 정책을 준비해야 한다. [첫 에이전트 실행](https://docs.nvidia.com/openshell/v0.1.2/about/run-your-first-agent)

## 3. 버전과 환경 조건

[공식 릴리스](https://github.com/NVIDIA/OpenShell/releases/tag/v0.1.2)에서 v0.1.2와 2026-09-28 배포를 확인했다. 조사 당시 latest도 v0.1.2였으며, 아래 링크는 가능하면 버전 경로로 고정했다. “alpha라서 모든 기능이 미지원”이라는 오래된 설명과 “stable release라서 모든 확장 인터페이스가 안정적”이라는 해석 모두 피한다.

| 환경 | 공식 조건 | 선택 시 확인 |
|---|---|---|
| Linux | Debian/Ubuntu x86_64·arm64 지원 | 배포용 1차 후보 |
| macOS | Apple Silicon 지원 | 로컬 개발 후보; Linux 경계 조건은 실제 VM/runtime에서 확인 |
| Windows | WSL2 + Docker Desktop x86_64는 Experimental | 행사 시간 안에 검증 가능한 경우만 사용 |
| Docker | Docker Desktop/Engine 28.0 이상 | 단일 서버 구성에 우선 검토 |
| Podman | 5.x, Linux cgroups v2·사용자 socket 등 필요 | rootless 운영 경험이 있을 때 검토 |
| Kubernetes | 1.29 이상, Helm 3.x 등 | 기존 클러스터가 있는 경우 검토; 본선용 신규 구축은 우선순위 낮음 |
| MicroVM | macOS Hypervisor.framework 또는 Linux KVM | 클라우드 nested virtualization/KVM 접근을 별도 확인 |
| Linux 보안 기능 | Landlock ABI 3 이상, seccomp user notification 등 | 일반적으로 Linux 6.2 이상 또는 적합한 backport; 커널 버전만으로 합격 처리하지 않음 |

OpenShell은 시작 시 필요한 경계 기능을 실제로 검사한다. `uname`이나 Docker 버전이 맞아도 Landlock 비활성화·seccomp 제한 등으로 시작이 거부될 수 있다. GPU는 별도 모델/도구가 요구할 때 선택하며 OpenShell 사용만으로 GPU 임대 필요성이 생기지는 않는다. [지원표·커널 조건](https://docs.nvidia.com/openshell/v0.1.2/about/support-matrix), [런타임](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/sandboxes/runtimes)

### 오래된 예제에서 달라진 부분

- 0.0.x와 0.1.x 구성요소를 섞지 않는다. gateway·CLI·SDK·driver 등 호환 버전을 함께 맞춘다.
- `gateway.toml`은 schema version 2로 변경됐다. **샌드박스 정책 YAML의 `version: 1`과는 다른 버전**이다.
- 기본 workload 이미지에는 에이전트 CLI가 포함돼 있지 않다. `openshell sandbox create`만으로 우리 서비스가 준비되지는 않는다.
- `--from ./Dockerfile`로 바로 빌드하는 오래된 절차 대신 이미지를 먼저 빌드하고 명시적 image reference를 사용한다.
- 모델 연결은 profile·provider attachment·실제 공급자 endpoint를 기준으로 구성한다. 과거 managed inference route 예제의 명령을 그대로 복사하지 않는다.

[0.1.0 변경 안내](https://docs.nvidia.com/openshell/v0.1.2/upgrade/0-1-0), [이미지와 생명주기](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/sandboxes/overview)

## 4. 보안정책의 구조

| YAML 구역 | 통제 대상 | 적용 시점 | 팀의 기본 방향 |
|---|---|---|---|
| `version: 1` | 정책 스키마 | 읽을 때 | 지원 스키마에 맞춤 |
| `filesystem_policy` | 읽기·쓰기 경로와 작업 디렉터리 | 시작 시 | 자료 읽기와 결과 쓰기 경로 분리 |
| `landlock` | 추가 파일 정책 적용 실패 시 처리 | 시작 시 | `compatibility: hard_requirement` 검토 |
| `process` | 실행 사용자·그룹 | 생성 시, Docker/Podman | 이미지와 일치하는 non-root identity |
| `network_policies` | 목적지·포트·실행 파일·요청 | 실행 중 변경 가능 | 최소 허용 목록과 명시적 `enforce` |
| `network_middlewares` | 허용된 트래픽의 추가 검사·변환·차단 | 실행 중 변경 가능 | 필요가 확인된 경우만 도입 |

정책은 전역 → 저장된 sandbox 정책 → 이미지 내 정책 → restrictive default 순으로 선택한다. 생성 시 명시한 `--policy`는 `OPENSHELL_SANDBOX_POLICY`보다 우선한다. Provider가 더하는 규칙까지 합친 **effective policy**를 확인해야 실제 권한을 알 수 있다.

전역 정책은 개별 정책 위에 제한을 덧씌우는 교집합이 아니라 **개별 정책을 대체**한다. 활성화 중에는 provider 추가 규칙도 억제하므로 모델 연결까지 영향을 받을 수 있다. [정책 개요](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/overview)

### 4.1 파일·프로세스

문화 자료는 읽기 전용 경로, 요청별 출력은 별도 쓰기 경로에 둔다. 모델 키·관리 인증서·호스트 홈·Docker socket을 workload에 넣지 않는 구성을 제안한다. Python/Node 등 실행에 필요한 라이브러리·임시 경로도 이미지와 대조한다.

`filesystem_policy`를 생략하면 작업 디렉터리를 쓰기 허용하지만, 구역을 작성하면 `include_workdir` 기본값이 false로 바뀐다. 이를 명시해야 작업 폴더 전체 쓰기가 의도치 않게 열리거나 필요한 쓰기가 막히는 일을 피할 수 있다. 읽기 경로 아래를 쓰기 경로가 겹쳐 덮는지도 확인한다.

`hard_requirement`도 존재하지 않거나 열 수 없는 개별 경로는 건너뛴다. 따라서 YAML에 적었다는 사실만으로 해당 파일 보호를 증명할 수 없다. 준비한 경로의 존재·실제 허용/차단·Landlock의 applied/skipped 로그를 함께 확인한다. Mandatory baseline과 추가 파일 정책의 적용 성공은 구분한다. [정책 스키마](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/schema), [기본 정책](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/default-policy)

### 4.2 통신: host 허용과 요청 허용을 분리

먼저 목적지 host·port·실행 파일이 허용되는지 확인하고, L7 프로토콜을 설정했다면 HTTP method/path 또는 해당 프로토콜의 요청을 검사한다. 같은 domain이 조회·등록·삭제 API를 모두 제공할 수 있으므로 domain만 열면 읽기 전용 서비스가 되지 않는다.

| 설정·상황 | 의미 | 설계 판단 |
|---|---|---|
| `protocol: rest` + 정확한 `rules` | method/path 등의 요청 검사 | 문화 자료 조회 API의 구체적인 GET 경로에 적용 가능 |
| `enforcement: audit` | 위반을 기록하지만 통과시킴 | 실제 차단 증거로 사용 불가 |
| `enforcement: enforce` | 허용 규칙에 맞지 않는 요청 차단 | 배포 정책에서 명시 |
| `access: read-only` | 프로토콜에 따른 읽기 preset | API가 GET으로 상태를 바꾸는지 등 업무 의미까지 보장하지 않음 |
| `tls: skip` | 암호화된 내용을 복호화·검사하지 않음 | L7 검사·credential 대체가 필요한 경로에 적용하지 않음 |
| 광범위한 host·binary glob | 접근 가능한 범위를 넓힘 | 실제 endpoint·설치 경로로 축소 |
| 허용 host의 redirect | 새 목적지 접근이 필요할 수 있음 | redirect/CDN 호스트도 목적과 권한을 별도 검토 |

`deny_rules`는 허용 규칙보다 우선한다. Binary 식별은 실행 파일과 실행 조상에 연결되므로 “curl만 막으면 Python을 통한 호출도 막힌다”고 가정하지 않는다. 허용된 Python 인터프리터가 여러 스크립트를 실행하는 경우, 스크립트별 업무 권한은 추가 검증이 필요하다. [네트워크 규칙](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/network-rules)

SSRF 방어가 있지만 명시한 내부 hostname·`allowed_ips` 등 정책 설정에 따라 내부 접근 범위가 달라진다. 공개 사용자가 임의 URL을 전달하는 기능을 만들 경우 애플리케이션에서도 URL·redirect·응답 크기를 검사한다. 샌드박스 내부 loopback 서비스와 외부 통신의 loopback 차단을 혼동하지 않는다. [보안 설정](https://docs.nvidia.com/openshell/v0.1.2/security/best-practices), [destination 스키마](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/schema)

### 4.3 Provider와 모델 호출

Provider profile은 자격증명 이름과 허용 endpoint·binary를 정의한다. Workload에는 opaque placeholder를 주고, 승인된 목적지로 나갈 때 supervisor가 실제 자격증명으로 대체한다. NVIDIA 모델도 profile을 검토·import한 뒤 provider를 생성하고 필요한 sandbox에만 attach한다.

Provider를 붙이면 네트워크 권한도 추가될 수 있다. Base policy만 검토하지 말고 `--full`로 effective policy를 확인한다. 모델 endpoint를 허용하는 것은 그 endpoint로 보낸 사용자 입력의 외부 전송도 허용하는 것이므로, 보내도 되는 자료를 서비스 수준에서 제한해야 한다.

현재 실행하지 않은 사항: 계정의 모델 접근 권한, 실제 model ID, 응답 형식, 비용·한도, credential 대체 성공. 저장소의 [모델 호출 한도](../../playbooks/model-policy.md)는 별도 애플리케이션 책임으로 계속 적용한다. [Inference](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/inference), [Providers](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/providers/overview)

### 4.4 정책 변경과 승인

1. 차단된 요청의 host·port·binary·필요 목적을 확인한다.
2. 필요한 권한만 제안하고 운영자가 검토한다. 서비스 이용자의 텍스트 요청을 정책 변경 권한으로 취급하지 않는다.
3. Base 정책을 수정하고 새 revision의 실제 적용 상태를 확인한다.
4. 같은 허용·차단 테스트를 재실행한다. 문제가 있으면 검토된 이전 base 정책을 새 revision으로 적용한다.

네트워크 규칙 변경 시 기존 연결이 닫히므로 streaming·keep-alive·WebSocket 재연결을 고려한다. 파일·identity 정책 변경은 재생성을 기준으로 계획한다. 유효하지 않은 새 정책의 runtime 적용 실패는 기본 `fail_closed`와 선택 가능한 `retain_last_valid`의 결과가 다르므로 운영 설정을 기록한다. [정책 관리](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/manage-policies)

Advisor의 기본 승인 방식은 `manual`이다. `auto`는 자격증명이 적용되지 않는 새 public host 접근도 자동 승인할 수 있다. 따라서 **외부 반출 차단을 시연하는 서비스에서는 manual을 유지**하는 것이 팀 제안이다. 자동 승인 위험 검사와 우리가 작성한 boundary에 대한 포함 관계 검사는 서로 다른 기능이다. [Policy Advisor](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/advisor)

### 4.5 Policy Prover의 효용과 한계

`openshell-prover check candidate.yaml --boundary boundary.yaml`은 candidate 권한이 정의한 boundary 안에 있는지 검사한다. 파일·프로세스·Landlock·L4/REST의 지원 범위를 검사하지만 모든 프로토콜을 증명하지는 않는다.

| 결과 | 처리 |
|---|---|
| `within_boundary` | 검사한 coverage 안에서만 통과 |
| `exceeds_boundary` | counterexample을 보고 정책 축소 |
| `error` | 입력·실행 실패 해결 후 재검사 |
| `unsupported` / `inconclusive` | 미검증; 통과로 바꾸지 않음 |

검사 통과는 boundary 자체의 적절성, 문화 정보의 정확성, 실제 sandbox의 정책 집행을 보장하지 않는다. GraphQL·MCP 등 선택한 정책 모양의 지원 여부도 확인한다. 공개 시연에서 “안전성 전체를 수학적으로 증명”했다고 표현하지 않는다. [Policy Prover](https://docs.nvidia.com/openshell/v0.1.2/how-it-works/policies/prover)

## 5. 한국 문화 주제에 적용할 정책 설계 예시

아래는 **‘검토한 문화 자료를 조회해 근거와 함께 설명하는 서비스’라는 가정 하나**를 사용한 예시다. 사용자가 확정한 제품이나 API 목록은 아니다.

| 자원/행동 | 제안 권한 | 검증할 것 |
|---|---|---|
| 검토한 문화 자료 `/workspace/sources` | 읽기 | 자료 조회 성공, 원본 수정 실패 |
| 요청별 `/workspace/output` | 읽기·쓰기 | 산출물 생성 성공, 다른 사용자 자료 노출 없음 |
| 문화 자료 API | 정한 binary에서 특정 host:443의 필요한 GET 경로만 | 정상 조회 성공, 같은 host의 쓰기 요청 거부 |
| 선택한 모델 API | Provider로 특정 endpoint·필요 요청만 | 실제 키 대신 placeholder, 모델 요청 성공 |
| 임의 외부 업로드·게시 endpoint | 미허용 | 반출 요청 거부와 수신 측 미수신 확인 |
| 정책·관리 키·다른 사용자 파일 | workload에 전달하지 않음 | 접근 불가, 정책 변경 권한 없음 |

상태 흐름은 ‘자료 조회 → 충분성 판단 → 필요한 도구 호출 → 실행 결과 검증 → 근거 있는 결과/자료 부족/정책상 제한’으로 둔다. 차단을 만나면 허용된 자료로 계속하거나 필요한 권한과 이유를 표시하고 보류한다. 같은 차단 요청을 무한 재시도하거나 자동으로 허용 host를 넓히지 않는다.

정책 이벤트는 제품의 핵심 흐름과 연결한다. “보안 작동 중” 배지만 표시하지 말고 어떤 작업이 허용·거부됐으며 사용자가 무엇을 할 수 있는지 보여준다. 정책 YAML 전체와 원본 운영 로그를 일반 이용자에게 노출할 필요는 없다.

## 6. 증거를 남길 최소 검증

| 검사 | 입력/행동 | 성공 기준 |
|---|---|---|
| 허용 파일 | 준비한 자료 읽기, 출력 폴더에 결과 생성 | 정확한 결과와 정상 종료 |
| 금지 파일 | 존재하는 테스트 파일 수정 시도 | permission 거부와 파일 hash 불변; 파일 부재 오류로 대체하지 않음 |
| 허용 네트워크 | 제어 가능한 정상 endpoint 조회 | 정상 응답과 허용 이벤트 |
| 미허용 목적지 | 팀이 관리하는 별도 수신 endpoint 접근 | 정책 deny와 해당 request ID 미수신; DNS 실패를 차단으로 오인하지 않음 |
| 허용 host의 금지 method/path | 테스트 서버의 비파괴 쓰기 경로 호출 | L7 거부, 서버 상태 불변 |
| 자격증명 보호 | 가짜 canary credential로 provider 연결 | workload에는 placeholder, 승인된 테스트 서버에서만 대체 확인 |
| 권한 확대 | 차단 후 advisor 제안 확인 | 승인 전 차단 유지; 공개 사용자가 승인할 수 없음 |
| 사용자 격리 | A/B 세션의 다른 입력·결과 접근 | 서로의 산출물·상태 접근 거부 |
| 정책 변경 | 좁은 규칙으로 갱신 후 재요청 | 새 revision 적용과 연결 재수립 확인 |
| 자료 속 지시문 | 문화 자료에 외부 전송 유도 문구를 넣은 합성 입력 | 금지 도구 실행 차단, 결과에 제한 이유 표시 |

검증은 실제 키·실제 사용자 자료 대신 합성 입력과 팀 소유 테스트 endpoint로 시작한다. 에이전트가 시도하지 않았거나 대상 서버 자체가 내려간 경우는 정책 차단 성공과 구분한다. 위 표 전체를 완료한 것은 아니며 실행된 최소 검사와 남은 범위는 [하네스 사용법](../../playbooks/openshell-harness.md)에 구분한다.

OCSF 기반 이벤트로 허용·거부와 원인을 확인할 수 있다. 서비스의 `run_id`와 sandbox 식별자·정책 revision·시각을 연결하고, 화면은 실제 이벤트를 요약해 표시한다. 사용자의 원문·키·credential 포함 query가 로그나 화면으로 새지 않는지도 확인한다. [로그 형식](https://docs.nvidia.com/openshell/v0.1.2/observability/logging)

## 7. OpenShell만으로 해결되지 않는 것

- 허용된 endpoint에 보낸 내용의 업무 적절성, 저작물 이용 범위, 문화 설명의 사실성·편향: 출처·응답·데이터 검토가 필요하다.
- 허용된 파일 범위 안에서의 잘못된 수정: 좁은 쓰기 경로와 결과 검증·복구가 필요하다.
- 서비스 로그인·세션 소유권·사용량 제한·요청 크기·동시 실행·비용: 서비스 백엔드에서 구현한다.
- 호스트 관리자·gateway·supervisor 등 신뢰 영역의 침해: 별도의 배포 보안과 권한 관리가 필요하다.
- 모든 프롬프트 인젝션의 예방: 실행 권한을 제한할 수 있지만 잘못된 답변이나 허용된 행동의 오용까지 없애는 것은 아니다.

## 8. 후속 정보로 결정할 사항

| 필요한 정보 | 결정되는 내용 |
|---|---|
| 대상 사용자·구체적 문화 분야·사용자 실패 상황 | Intent·핵심 작업·완료 기준 |
| 동료평가 세부 산식·추가 테스트 조건 | 공식 큰 배점은 확보; 실제 검사·집계의 세부 사항 확인 |
| 데이터·API·사용자 업로드 여부 | filesystem·host·method/path·provider 범위 |
| 접속 대상·로그인 허용·동시 사용자·유지 기간 | 공개 방식·격리 단위·자원·종료 시점 |
| Brev 계정·크레딧 또는 별도 서버 조건 | 실행 환경 선택과 비용 상한 |

추가 정보가 오면 이 문서의 정책 원칙을 실제 endpoint·파일 경로·검증 입력으로 구체화한다. OpenShell 필수 조건은 유지하고 설치가 지연되면 다른 runtime으로 필수 도구를 대체하는 대신 작업 범위와 호스트 구성을 줄인다.
