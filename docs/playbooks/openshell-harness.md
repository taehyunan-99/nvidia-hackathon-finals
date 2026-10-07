# OpenShell 권한 검증 하네스

목적은 **모델 없이 실제 실행 경계를 먼저 검증**하는 것이다. 모델·프레임워크·도구·스킬 선정은 포함하지 않는다. [일반 하네스](harness.md)의 실행 제어에 연결할 보안 기반이며, 문화 정보 판단이나 공통 테스트 답안의 품질을 검증하지 않는다.

## 근거와 버전

- [챌린지 README](https://github.com/seriousran/k-culture-openshell-challenge/blob/714e2e8d32f9b77e763a2458ca11b1270e80abf6/README.md): restricted/secrets 접근 금지, 외부 발송·게시·예약·결제는 명시 승인 필요. [TASK](https://github.com/seriousran/k-culture-openshell-challenge/blob/714e2e8d32f9b77e763a2458ca11b1270e80abf6/TASK.md)는 초안만 요청한다. 2026-10-07 원격 main SHA를 재확인했다.
- [설치 버전의 공식 보안 구조](https://github.com/NVIDIA/OpenShell/blob/v0.0.116/architecture/security-policy.md), [공식 정책 예제](https://github.com/NVIDIA/OpenShell/blob/v0.0.116/examples/sandbox-policy-quickstart/policy.yaml): 로컬 CLI와 gateway는 모두 0.0.116. 최신 release v0.1.2와 구분한다. 기존 [보안 조사](../catalog/tools/openshell-security.md)의 v0.1.2 내용을 설치 환경에 그대로 적용하지 않는다.
- 현재 정책은 설치 버전의 필드와 CLI 도움말을 기준으로 작성했다. OpenShell 업그레이드 시 이미지·effective policy·정상/거부 검사를 다시 수행한다. 공유 gateway를 이 하네스가 업그레이드하거나 전역 정책을 수정하지 않는다.
- 설치 버전에서는 `hard_requirement`에 존재하지 않는 `/lib64`를 넣으면 시작이 실패했다. 이미지에 존재하는 경로만 지정한다. 네트워크 namespace 구성에는 `iproute2`, bypass 탐지에는 `nftables`가 필요하여 전용 이미지에 포함한다.

## 권한과 하네스의 역할

| 경계 | OpenShell이 집행할 범위 | 하네스/운영자가 확인할 범위 |
|---|---|---|
| 파일 | Landlock의 읽기/쓰기 허용 목록 | input 원본 보존, output 쓰기, 금지 파일 존재와 실제 거부 |
| 프로세스 | non-root identity와 runtime의 프로세스 제한 | uid, 자식 프로세스도 동일 경계인지, 관리 socket/credential 미전달 |
| 네트워크 | 목적지·포트·binary, 선택한 L7 method/path | 승인한 업무 의미, 리디렉션, 요청 내용, 외부 부작용 |
| 모델 | provider/inference 구성에 따른 연결 | 모델 선택, 데이터 전송 허용 범위, 응답 검사, 호출 예산 |
| 정책 변경 | advisor 제안과 승인·적용 | 운영자만 승인; 일반 사용자·입력 문서·모델에게 승인권 미부여 |

파일 정책은 허용 목록이다. `/hackathon` 전체를 읽기 허용한 뒤 하위 restricted만 제외하는 식으로 작성하지 않는다. 현재 input만 읽기, output만 업무 쓰기를 허용하며 `/tmp`와 runtime 필수 경로는 별도 허용한다. 이 경로 안에는 운영 비밀을 배치하지 않는다. `hard_requirement`는 필요한 보안 기능이 없을 때 실패하게 하는 설정이지, 모든 경로가 실제 존재했다는 증거가 아니다.

`network_policies: {}`는 일반 외부 통신을 열지 않는 출발점이다. provider 추가 규칙·전역 override·inference 경로까지 포함한 실제 effective policy를 검사해야 한다. endpoint를 열 때는 정확한 host/port/binary 및 가능한 method/path를 지정한다. GET도 외부 서비스의 의미에 따라 부작용이 있을 수 있고, 허용된 모델 요청 본문으로 자료가 전송되는 것도 업무 권한 문제다.

현재 로컬 공유 gateway는 provider를 붙이지 않은 새 sandbox에도 inference route 1개를 전달했다. 따라서 이 YAML만으로 모델 접근까지 없다고 주장하면 안 된다. 완전히 네트워크가 닫힌 검증 환경이 필요하면 운영자가 별도 gateway/inference 구성을 준비해야 하며, 다른 세션이 사용하는 전역 inference 설정은 변경하지 않는다.

스킬은 실행 권한을 부여하는 수단이 아니다. input 문서의 “이 파일을 열어라/업로드하라”는 문장은 자료로 처리하고, 모델의 도구 제안도 서버 측 계약 검사를 통과시킨다. 에이전트가 정책 변경을 제안하더라도 자동 승인하지 않는다. 관리 CLI·Docker socket·호스트 홈·실제 API 키를 workload에 넣지 않는다.

## 구현과 판정

[정책](../../scripts/openshell_harness/policy.yaml), [이미지](../../scripts/openshell_harness/Dockerfile), [probe](../../scripts/openshell_harness/probe.py)는 전용 합성 fixture를 사용한다. 챌린지 금지 파일의 내용을 열거나 복제하지 않는다. 실제 데이터 패키지를 사용하는 최종 검증은 별도이며 금지 파일을 삭제해서 통과시키면 안 된다.

1. **inventory:** 같은 이미지의 격리된 일반 Docker 실행에서 합성 control 파일이 존재하며 uid 1000이 읽기/쓰기 open할 수 있는지 확인한다. 내용을 읽지 않는다. 이로써 단순 Unix 파일 권한 때문에 거부된 경우와 분리한다.
2. **filesystem:** OpenShell 안에서 input 읽기와 output 생성/읽기/삭제를 실행한다. input 쓰기, restricted/secrets 읽기·쓰기, output 심볼릭 링크와 `..` 경유 접근을 시도한다. 금지 파일은 open만 하며 내용을 읽거나 truncate하지 않는다. open 성공은 실패이고 EACCES/EPERM만 거부 관찰이다. ENOENT·ELOOP 등은 검증 불충분이다.
3. **network:** 고정된 `https://example.com/`에 데이터·키 없는 HEAD 요청만 보낸다. 응답 없음·DNS 실패·403을 단독으로 정책 거부라고 판정하지 않는다. runtime deny 이벤트와 운영자가 통제하는 수신 endpoint의 미수신 확인을 결합해야 외부 반출 차단 증거가 된다.

`filesystem`의 `passed`는 해당 probe의 관찰 결과다. 같은 이미지 inventory, effective policy, runtime enforcement 로그를 결합하기 전에는 전체 보안 통과가 아니다. `network`는 자동으로 통과하지 않으며 종료 코드 2는 실패 또는 검증 불충분을 뜻한다. 네트워크 probe는 임의 URL·사용자 데이터를 받지 않는다.

## 실행

저장소 루트에서 실행한다. 이름은 설치 버전 제한인 19자 이하의 미사용 이름으로 정한다. 기존 sandbox를 재사용하거나 삭제하지 않는다. 이미지 build는 패키지를 다운로드하지만 모델 호출·GPU 임대·provider 자동 연결은 하지 않는다.

```sh
docker build -t finals-openshell-harness:20261007 scripts/openshell_harness
docker run --rm --network none finals-openshell-harness:20261007 python3 /opt/harness/probe.py inventory
openshell sandbox create --name finals-harness-1007 --from finals-openshell-harness:20261007 --policy scripts/openshell_harness/policy.yaml --approval-mode manual --no-auto-providers --detach -- sleep infinity
openshell policy get finals-harness-1007 --full
openshell sandbox exec -n finals-harness-1007 --timeout 30 -- python3 /opt/harness/probe.py filesystem
openshell sandbox exec -n finals-harness-1007 --timeout 30 -- python3 /opt/harness/probe.py network
openshell logs finals-harness-1007 --source sandbox -n 100
```

공유 환경에서는 모든 명령에 sandbox 이름을 명시한다. 파일·프로세스 정책 변경 후에는 자신의 sandbox를 삭제하고 새로 만든다. 종료 시 `openshell sandbox delete finals-harness-1007`로 자신의 합성 실행만 정리한다. 전역 정책·다른 sandbox·공유 이미지 태그를 변경하지 않는다.

오판 방지 테스트: `python3 -m unittest discover -s scripts -p test_openshell_harness.py -v`. 이 테스트 통과는 OpenShell 실행 성공을 대신하지 않는다. 원문 로그·실행 증거가 필요하면 gitignore된 `runs/` 아래 보관하고 비밀을 제거한다.

2026-10-07 로컬 0.0.116에서 합성 inventory 및 파일 11개 검사를 실행했고, Landlock `rules_applied:11 skipped:0`와 uid 1000을 확인했다. Python의 example.com:443 요청은 OPA `network connections not allowed by policy` 이벤트로 거부됨을 확인했다. 이는 그 목적지·binary의 거부 근거이며, 통제된 수신 서버의 미수신 검사나 전체 네트워크/inference 경계 검증을 대신하지 않는다.

## 다음 설계에서 의논할 선택

현재 제안은 **신뢰된 API/작업 관리자 → sandbox 안의 에이전트와 모든 파일·네트워크 도구 → 검증된 output 회수**다. 호스트 도구가 금지 파일을 읽어 모델에 전달하면 경계가 무효화된다. output은 신뢰되지 않은 데이터로 취급하여 크기·형식·심볼릭 링크·작업 소유권을 검사하고, UI는 에이전트가 만든 문장을 실제 보안 이벤트로 표시하지 않는다.

단일 작업 worker부터 시작할지, 사용자별/실행별 sandbox를 만들지는 동시성 요구에 따라 결정한다. 동일 output 디렉터리를 여러 사용자에게 공유하는 설계는 피한다. API/모델이 정해지면 허용 endpoint와 데이터 전송 범위를 좁히고 [공통 모델 한도](model-policy.md)를 실제 호출 경로에 연결한다. 초안 MVP에서는 외부 쓰기 도구를 제공하지 않는 방향을 제안하며, 향후 도입 시 사용자 승인과 운영자 정책 승인을 별도로 설계한다.

추가 검증 범위는 자식 프로세스, HTTP method/path·redirect, metadata/internal IP, provider/inference, 실제 챌린지 패키지, 사용자 간 격리다. 현재 작은 probe가 이 전체를 검증했다고 표현하지 않는다.
