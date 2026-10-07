# OpenShell 권한 검증 하네스

목적은 **모델 없이 실제 실행 경계를 먼저 검증**하는 것이다. 모델·프레임워크·도구·스킬 선정은 포함하지 않는다. [일반 하네스](harness.md)의 실행 제어에 연결할 보안 기반이며, 문화 정보 판단이나 공통 테스트 답안의 품질을 검증하지 않는다.

## 근거와 버전

- [챌린지 README](https://github.com/seriousran/k-culture-openshell-challenge/blob/714e2e8d32f9b77e763a2458ca11b1270e80abf6/README.md): restricted/secrets 접근 금지, 외부 발송·게시·예약·결제는 명시 승인 필요. [TASK](https://github.com/seriousran/k-culture-openshell-challenge/blob/714e2e8d32f9b77e763a2458ca11b1270e80abf6/TASK.md)는 초안만 요청한다. 2026-10-07 원격 main SHA를 재확인했다.
- [설치 버전의 공식 보안 구조](https://github.com/NVIDIA/OpenShell/blob/v0.0.116/architecture/security-policy.md), [공식 정책 예제](https://github.com/NVIDIA/OpenShell/blob/v0.0.116/examples/sandbox-policy-quickstart/policy.yaml): 로컬 CLI와 gateway는 모두 0.0.116. 최신 release v0.1.2와 구분한다. 기존 [보안 조사](../catalog/tools/openshell-security.md)의 v0.1.2 내용을 설치 환경에 그대로 적용하지 않는다.
- 현재 정책은 설치 버전의 필드와 CLI 도움말을 기준으로 작성했다. OpenShell 업그레이드 시 이미지·effective policy·정상/거부 검사를 다시 수행한다. 공유 gateway를 이 하네스가 업그레이드하거나 전역 정책을 수정하지 않는다.
- 확장 검사는 Brev의 CLI·gateway **0.1.2**에서도 별도 합성 이미지로 확인했다. 원격 호스트에서 이미지를 빌드하며, 비대화형 실행에는 `sandbox exec`의 `--no-tty`를 사용한다. 로컬 ARM 이미지·0.0.116 검사를 원격 x86_64·0.1.2 증거로 대신하지 않는다.
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
2. **filesystem:** OpenShell 안에서 input 읽기와 output 생성/읽기/삭제를 실행한다. input 쓰기, restricted/secrets 읽기·쓰기, output 심볼릭 링크와 `..` 경유 접근을 시도한다. 같은 Python의 자식 프로세스로 input 쓰기와 금지 파일 읽기를 재시도하고 허용 input의 전후 hash를 비교한다. 총 15개 관측이며 금지 파일은 open만 하고 내용을 읽거나 truncate하지 않는다. open 성공은 실패이고 EACCES/EPERM만 거부 관찰이다. ENOENT·ELOOP·자식 실행 실패는 검증 불충분이다.
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
openshell sandbox exec -n finals-harness-1007 --timeout 30 -- python3 /opt/harness/output_probe.py
openshell sandbox exec -n finals-harness-1007 --timeout 30 -- python3 /opt/harness/probe.py network
openshell logs finals-harness-1007 --source sandbox -n 100
```

공유 환경에서는 모든 명령에 sandbox 이름을 명시한다. 파일·프로세스 정책 변경 후에는 자신의 sandbox를 삭제하고 새로 만든다. 종료 시 `openshell sandbox delete finals-harness-1007`로 자신의 합성 실행만 정리한다. 전역 정책·다른 sandbox·공유 이미지 태그를 변경하지 않는다.

오판 방지·결과 회수 테스트: `python3.11 -m unittest discover -s scripts -p 'test_openshell*.py' -v`. 이 테스트 통과는 OpenShell 실행 성공을 대신하지 않는다. 원문 로그·실행 증거가 필요하면 gitignore된 `runs/` 아래 보관하고 비밀을 제거한다.

2026-10-07 로컬 0.0.116에서 합성 inventory 및 파일 11개 검사를 실행했고, Landlock `rules_applied:11 skipped:0`와 uid 1000을 확인했다. Python의 example.com:443 요청은 OPA `network connections not allowed by policy` 이벤트로 거부됨을 확인했다. 이는 그 목적지·binary의 거부 근거이며, 통제된 수신 서버의 미수신 검사나 전체 네트워크/inference 경계 검증을 대신하지 않는다.

확장된 하네스는 2026-10-07 Brev 0.1.2에서 inventory·파일 경계 15개·합성 결과 회수 12개를 통과했다. UID 1000, provider 미부착, effective policy, 실제 컨테이너 image ID 및 세 Python 소스 hash 일치, Landlock `rules_applied:14 skipped:0`를 대조했다. CLI 로그가 비어 있으면 해당 sandbox에 대응하는 workload 컨테이너의 로그에서 집행 이벤트를 확인한다. 이 근거는 합성 파일·회수 함수의 검사이며 실제 챌린지 패키지·제품 모델/API·웹 인증·외부 반출 검사를 통과했다는 뜻은 아니다.

## 결과를 회수하는 경계

[회수 함수](../../scripts/openshell_harness/output.py)는 모델과 독립적으로 호출한다. 관리자가 연 output 루트의 디렉터리 FD, 서버 장부의 작업 ID·소유자, 인증된 요청자와 예상 파일 UID를 전달한다. 모델 응답의 owner 필드를 권한 근거로 사용하지 않는다. 다른 작업의 출력이 쓰기 가능한 공유 mount는 만들지 않는다.

작업 디렉터리 이름은 서버가 생성한 32자리 소문자 hex ID이며 읽는 파일은 `result.json`으로 고정한다. 모든 하위 open은 디렉터리 FD에 상대적으로 수행하고 symlink를 따라가지 않는다. FIFO·디렉터리·하드링크·UID 불일치·크기 초과·읽는 동안의 변경·잘못된 UTF-8/JSON·중복 키·비유한 수를 거부한다. 최대 크기는 기본 64 KiB이며 메모리에 읽기 전과 읽는 도중에 검사한다. 예외는 원문·경로를 포함하지 않는 고정 사유 코드만 반환한다.

전송 외피는 `{"job_id":"서버 작업 ID", "result":{...}}`다. `result` 내부의 제품 schema는 아직 확정하지 않으며 소비자가 별도로 검증해야 한다. 공통 테스트의 자유 산출물 형식을 제한하는 계약이 아니다. 이 함수는 내용의 정확성·비밀 탐지·HTML 안전성이나 웹 세션 인증을 증명하지 않는다.

**회수 전 필수 조건:** 관리자가 실제 writer 종료를 확인하고 해당 작업의 output만 회수한다. 파일 변경 감지는 보조 검사이며 실행 중인 악성 writer와의 모든 경쟁을 해결하지 않는다. sandbox 안의 [합성 회수 검사](../../scripts/openshell_harness/output_probe.py)는 정상 회수와 잘못된 소유자/작업·UID·크기·JSON·UTF-8·파일 부재·symlink·하드링크·FIFO 12개를 검사한다. 실제 호스트 수집기·웹 인증과의 통합은 별도다.

## 에이전트 연결 전후의 권한 계약

| 모드 | 업무 도구 | 외부 통신 |
|---|---|---|
| 합성 경계 검사 | 운영자 전용 고정 probe | 기본 미허용; 기존 HEAD 검사만으로 자동 PASS 불가, 아래 통제 수신처 검사로 보완 |
| 챌린지 | 허용 input 검색·읽기와 실행별 output 저장 | 검증된 모델 추론 endpoint만; 실제 연결 전 미허용 유지 |
| 두루 | 후보·상세·허용 출처 ID 조회 | 검증된 모델·서울 API·공식 안내 경로만; 모델과 자료 provider 분리 |

뒤 두 모드의 최종 정책은 모델·endpoint·NAT 이미지가 확정된 뒤 작성한다. 현재 파일은 모델 없는 합성 baseline이다. input 원본은 읽기만, 코드·의존성은 읽기만, 업무 쓰기는 작업별 output으로 제한하고 non-root·`hard_requirement`를 유지한다. 모델·요청 파일이 command/image/policy/provider를 선택하거나 정책을 확대하지 못하게 한다. 실제 경계 검사에서는 base/effective policy와 provider·전역 override를 대조한다. provider가 추가한 권한은 별도 확인하며 로컬 0.0.116의 inference route를 원격 0.1.2의 모델 경로로 해석하지 않는다.

도구 인자·redirect·출처·결과 검증과 공통 요청 예산은 애플리케이션 책임이다. 단위 검사의 가짜 모델/도구와 실제 모델 실행 근거를 구분한다. 모델/API를 허용한 제품 정책의 반출 재검사, 실제 사용하는 키의 비노출, 에이전트의 자료 속 지시 처리·조건 변경·종료 확인은 후속 통합 검증으로 남는다.

## 본선용 최소 네트워크 검사

[network_probe.py](../../scripts/openshell_harness/network_probe.py)는 운영자가 소유한 private IPv4 수신기에 고정된 비민감 합성 표식만 POST한다. 사용자 자료·금지 파일·키를 입력받지 않고 redirect를 따르지 않는다. 수신기는 받은 내용이나 헤더를 저장하지 않고 POST 횟수와 정확한 합성 표식 수신 횟수만 센다. 외부 공개 포트·새 클라우드 자원·범용 공격 시험은 필요 없다.

1. Brev에서 이 하네스 이미지로 임시 Docker 수신기를 실행한다: `python3 /opt/harness/network_probe.py serve`. Docker bridge에만 연결하고 `-p`로 포트를 공개하지 않는다. 운영자가 `docker inspect`로 얻은 수신기 IP의 `8080`만 사용한다.
2. 같은 호스트에서 proxy를 거치지 않고 `/probe`에 `OPENSHELL_SYNTHETIC_BOUNDARY_PROBE_V1`을 POST하여 정상 수신을 확인한다. `/health`의 `posts=1, accepted=1`을 대조 기준으로 저장한다.
3. provider 없는 새 sandbox에 기존 baseline 정책을 적용한 후 `python3 /opt/harness/network_probe.py attempt --receiver <수신기-IP>`를 실행한다. 그 목적지를 정책에 허용하지 않는다. proxy 설정은 유지하며 결과의 `unconfirmed` 또는 HTTP 403만으로 성공 처리하지 않는다.
4. 같은 sandbox·대상 IP/port·이번 시도에 대응하는 실제 정책 거부 이벤트, 수신 횟수 불변, 수신기 ID·시작 시각·restart 횟수 불변을 함께 확인한다. `verdict()`는 이 증거가 모두 갖춰진 경우에만 PASS이며 실제 도착은 FAIL, 수신기 장애·reset·근거 부족은 UNVERIFIED다. 검사가 끝나면 이번 수신기와 sandbox만 제거한다.

이는 sandbox 밖의 동일 Brev 내부 수신처에 대한 차단 증거다. 공개 인터넷의 모든 경로, 모델/API를 허용한 제품 정책, provider 비노출 또는 에이전트 판단의 검증으로 확대하지 않는다. 본선 범위에서는 이 한 사례를 먼저 사용하고 실제 endpoint 연결 시 같은 실행 정책으로 재검사한다.

2026-10-07 Brev OpenShell 0.1.2의 provider 없는 baseline에서 정상 대조 1건 수신 후 sandbox의 합성 POST 1건이 `transparent_tcp_policy_denied`로 거부됐다. 같은 수신기의 ID·시작 시각·restart 횟수가 유지됐고 수신 횟수도 1건 그대로였다. 따라서 해당 시도의 결과는 PASS이며 검증용 sandbox·수신기는 이후 제거했다.

## 다음 설계에서 의논할 선택

2026-10-07 사용자 확인으로 에이전트 구현 전 최소 보안 하네스의 독립 개발은 마쳤다. 추가 기능 개발 없이 남은 통합 조치는 다음 세 가지다.

1. **실제 패키지 보존·배치:** 챌린지의 input·restricted·secrets 원본을 보존해 정해진 `/hackathon` 경로에 배치한다. 합성 control의 통과를 실제 패키지 검사로 대신하지 않는다.
2. **팀원 에이전트·결과 회수 연결:** 에이전트와 모든 자료 도구를 OpenShell 안에서 실행하고, 작업 관리자가 writer 종료·작업 소유권을 확인한 뒤 결과 회수 함수를 호출한다. 제품 결과 schema 검증은 소비자와 맞춘다.
3. **같은 정책에서 재검증·실행 절차 정리:** 최종 이미지·provider 포함 실제 적용 정책에서 정상 과업·추가 조건·금지 접근·미승인 반출을 함께 재검증한다. 자료 속 지시 처리도 확인하고, 팀원·심사자가 재현할 입력 배치·실행·결과 확인 절차를 정리한다.

현재 제안은 **신뢰된 API/작업 관리자 → sandbox 안의 에이전트와 모든 파일·네트워크 도구 → 검증된 output 회수**다. 호스트 도구가 금지 파일을 읽어 모델에 전달하면 경계가 무효화된다. output은 신뢰되지 않은 데이터로 취급하여 크기·형식·심볼릭 링크·작업 소유권을 검사하고, UI는 에이전트가 만든 문장을 실제 보안 이벤트로 표시하지 않는다.

단일 작업 worker부터 시작할지, 사용자별/실행별 sandbox를 만들지는 동시성 요구에 따라 결정한다. 동일 output 디렉터리를 여러 사용자에게 공유하는 설계는 피한다. API/모델이 정해지면 허용 endpoint와 데이터 전송 범위를 좁히고 [공통 모델 한도](model-policy.md)를 실제 호출 경로에 연결한다. 초안 MVP에서는 외부 쓰기 도구를 제공하지 않는 방향을 제안하며, 향후 도입 시 사용자 승인과 운영자 정책 승인을 별도로 설계한다.

본선 우선 범위는 이 최소 하네스를 실제 에이전트·선택한 endpoint에 연결하고 챌린지 정상 과업·금지 접근·미승인 전송·자료 속 지시를 함께 검증하는 것이다. 범용 provider 시험 체계, 다양한 redirect 공격군, 복잡한 공유 예산 서비스·취소 복구 시스템은 이번 구현 범위에서 제외한다. 실제 연결에서는 사용하는 키의 비노출, 기존 호출 상한·timeout·종료 동작만 우선 확인한다.
