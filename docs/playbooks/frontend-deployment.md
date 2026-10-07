# 두루 프런트 수동 배포

공개 주소: [두루](https://d25wpps17lj0dn.cloudfront.net/). 공개 대상은 실제 OpenShell 가족 에이전트에 연결된 프런트다. 합성 실행 진입점은 제거했다. 전체 검색·잔여석·예약 확정은 제공하지 않는다.

## 구성

기존 서울 EC2 `i-0a6dced25ec8152c1`과 CloudFront `E39KLZ3QCHMW5G`를 재사용한다. CloudFront 기본 도메인·인증서로 브라우저 HTTPS와 HTTP→HTTPS 전환을 제공한다. 도메인 구매나 별도 인증서 발급은 필요 없다. EC2·전송·CloudFront 사용량 전체가 무료라는 의미는 아니다. [AWS HTTPS 설정](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-procedures.html).

CloudFront → 기존 Caddy 80번 → 전용 Docker 네트워크 `duru-edge` → `duru-frontend` 순서다. CloudFront는 서버 전용 요청 헤더를 붙이며 Caddy와 nginx가 이를 확인한다. EC2의 기존 CloudFront 전용 ingress를 유지하고 두루의 8080번은 localhost에만 연다. CloudFront→EC2 구간은 현재 HTTP다. 서버 API·사용자 민감 데이터를 연결하기 전 origin HTTPS를 별도로 구성해야 한다. [AWS origin 접근 제한](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/restrict-access-to-load-balancer.html).

기존 예선 컨테이너·API·Brev SSH 터널은 유지한다. Caddy 설정에 두루 전용 분기만 추가하고 기존 분기는 보존한다. 예선의 중지된 CloudFront 주소를 두루로 전환했으므로 해당 공개 주소는 이제 두루 화면이다. CloudFront의 기존 origin 설정은 보존한다.

## 실제 API 연결

`/api/*`는 캐시를 끄고 POST/DELETE와 `X-Run-Owner`를 전달한다. CloudFront의 별도 `duru-api` origin은 HTTPS를 사용한다. 현재 발표용 origin은 AWS의 `duru-api-origin.service`가 제공하는 Cloudflare Quick Tunnel이다. nginx는 기존 서버 전용 요청 헤더를 검사하므로 터널 주소만으로 API에 접근할 수 없다. [Quick Tunnel 공식 안내](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)는 이 경로를 임시 개발·시연 용도로 한정한다. 프로세스 재시작 시 origin 주소가 바뀌므로 공개 주소의 API origin을 갱신해야 한다. 지속 운영에는 고정 HTTPS origin으로 교체한다.

nginx → Docker host의 172.17.0.1:28081 → AWS `duru-agent-tunnel.service`의 인증 SSH → Brev 127.0.0.1:8001 → `duru-progress-forward.service` → OpenShell `family-progress` 8000 → 실제 API 순서다. Brev의 `duru-progress-api.service`가 단일 API worker를 감독한다. 기존 예선/bridge 서비스와 터널은 보존했다. 공개 ingress 포트와 새 VM은 추가하지 않았다.

제품 sandbox는 `finals-family-agent:progress` 이미지와 `agent/policy.yaml`, 기존 전용 NVIDIA provider를 사용한다. `agent/Web.Dockerfile`은 기존 검증된 base 위에 최신 코드만 설치한다. 이전 API를 종료한 뒤 일일 장부를 그대로 복사했다. 이전 `family-agent-mvp`·`family-agent-web`의 API는 정지 상태다. 이전 sandbox/CLI를 다시 실행하기 전 현재 제품 장부와 운영 집계를 대조해야 하며 동시 실행·장부 초기화는 금지한다.

지도 Client ID는 `frontend/.env.local`에서 읽어 서버 환경으로 전달한다. Client Secret은 전송하지 않는다. Maps Web 서비스 URL에 공개 도메인을 추가하고 저장해야 한다.

## 이후 배포

Python 3.11+, AWS CLI의 `her2-dev` 프로필, Docker, 기존 EC2 배포 키와 검증된 known_hosts가 필요하다. 저장소 루트에서 명시적으로 실행한다. 현재 작업 트리의 프런트를 빌드하며 Git 변경·병합·push만으로 실행되지 않는다.

```sh
python3 scripts/deploy_frontend.py \
  --ssh-key /배포키/경로 \
  --known-hosts /검증된/known_hosts \
  --host-key-alias 15.164.174.7
```

API origin 주소가 변경되면 같은 수동 명령에 `--api-origin <새 HTTPS 호스트명>`을 추가한다. CloudFront `Deployed`, `/api/health`, 실제 POST→소유권 GET→후보·근거·지도 표시를 확인한다. 터널·worker 장애 시 해당 systemd 서비스를 확인하고, API origin 터널을 재시작했다면 새 주소를 먼저 반영한다.

호스트 키 별칭은 최초 등록 때 사용한 주소다. 접속 주소는 AWS에서 매번 조회하지만 검증한 서버 키를 유지한다. 임의로 `StrictHostKeyChecking`을 끄지 않는다. 최초 CloudFront 연결에서만 `--init`을 사용했다. 이후에는 위 수동 명령만 사용한다. GitHub workflow·webhook 배포 연동은 추가하지 않았다.

스크립트는 Linux amd64 이미지를 빌드·전송하고 후보 컨테이너의 health를 확인한 뒤 교체한다. 직전 컨테이너는 `duru-rollback`으로 남기며 새 컨테이너 health 실패 시 복원한다. CloudFront invalidation 이후 실제 주소에서 화면과 자산을 확인한다. 제출 메시지는 전파 완료를 뜻하지 않으므로 CloudFront `Deployed` 상태와 HTTPS 응답을 확인한다.

`runs/duru-deployment.json`은 0600 권한의 로컬 운영 상태이며 요청 헤더와 기존 CloudFront 설정을 포함한다. Git에 넣거나 내용을 출력하지 않는다. 같은 체크아웃에서 보존한다. 서버에는 `/opt/duru/origin.env`와 원래 Caddy 설정 `/opt/duru/original.Caddyfile`을 보관한다. 운영 상태를 삭제해서 초기화하거나 키를 프런트 환경변수로 전달하지 않는다.

## 복구·운영 경계

수동 복구는 새 두루 컨테이너를 중지한 뒤 `duru-rollback`을 `duru-frontend`로 이름 변경·기동한다. 초기 공개 경로 자체를 되돌릴 때는 저장한 CloudFront 설정과 Caddy 원본을 사용하고, 기존 예선 서비스·터널을 중지하지 않는다. 예선 웹 컨테이너를 재생성하면 새 컨테이너를 `duru-edge`에 다시 연결해야 한다.

AWS의 기존 `bio3-stop.timer`는 2026-10-28 00:12 KST에 서버를 중지한다. 타이머를 변경하지 않았으며 서버 중지 후 두루도 접속되지 않는다. 운영 기간 연장은 별도 운영 결정이다.

포트 추가 조사 중 생성한 보안 그룹 `sg-06d78c025b58a30a0`은 ingress가 없고 인스턴스에 연결되지 않았다. 현재 계정의 삭제 권한이 없어 관리자 정리가 남았다. 실제 배포는 해당 그룹을 사용하지 않는다.
