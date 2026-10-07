# 두루 프런트 수동 배포

공개 주소: [두루](https://d25wpps17lj0dn.cloudfront.net/). 현재 공개 대상은 합성 예시 데이터로 동작하는 프런트다. 실제 에이전트·공식 API·OpenShell과의 연결 성공을 뜻하지 않는다.

## 구성

기존 서울 EC2 `i-0a6dced25ec8152c1`과 CloudFront `E39KLZ3QCHMW5G`를 재사용한다. CloudFront 기본 도메인·인증서로 브라우저 HTTPS와 HTTP→HTTPS 전환을 제공한다. 도메인 구매나 별도 인증서 발급은 필요 없다. EC2·전송·CloudFront 사용량 전체가 무료라는 의미는 아니다. [AWS HTTPS 설정](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cnames-and-https-procedures.html).

CloudFront → 기존 Caddy 80번 → 전용 Docker 네트워크 `duru-edge` → `duru-frontend` 순서다. CloudFront는 서버 전용 요청 헤더를 붙이며 Caddy와 nginx가 이를 확인한다. EC2의 기존 CloudFront 전용 ingress를 유지하고 두루의 8080번은 localhost에만 연다. CloudFront→EC2 구간은 현재 HTTP다. 서버 API·사용자 민감 데이터를 연결하기 전 origin HTTPS를 별도로 구성해야 한다. [AWS origin 접근 제한](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/restrict-access-to-load-balancer.html).

기존 예선 컨테이너·API·Brev SSH 터널은 유지한다. Caddy 설정에 두루 전용 분기만 추가하고 기존 분기는 보존한다. 예선의 중지된 CloudFront 주소를 두루로 전환했으므로 해당 공개 주소는 이제 두루 화면이다. CloudFront의 기존 origin 설정은 보존한다.

## 이후 배포

Python 3.11+, AWS CLI의 `her2-dev` 프로필, Docker, 기존 EC2 배포 키와 검증된 known_hosts가 필요하다. 저장소 루트에서 명시적으로 실행한다. 현재 작업 트리의 프런트를 빌드하며 Git 변경·병합·push만으로 실행되지 않는다.

```sh
python3 scripts/deploy_frontend.py \
  --ssh-key /배포키/경로 \
  --known-hosts /검증된/known_hosts \
  --host-key-alias 15.164.174.7
```

호스트 키 별칭은 최초 등록 때 사용한 주소다. 접속 주소는 AWS에서 매번 조회하지만 검증한 서버 키를 유지한다. 임의로 `StrictHostKeyChecking`을 끄지 않는다. 최초 CloudFront 연결에서만 `--init`을 사용했다. 이후에는 위 수동 명령만 사용한다. GitHub workflow·webhook 배포 연동은 추가하지 않았다.

스크립트는 Linux amd64 이미지를 빌드·전송하고 후보 컨테이너의 health를 확인한 뒤 교체한다. 직전 컨테이너는 `duru-rollback`으로 남기며 새 컨테이너 health 실패 시 복원한다. CloudFront invalidation 이후 실제 주소에서 화면과 자산을 확인한다. 제출 메시지는 전파 완료를 뜻하지 않으므로 CloudFront `Deployed` 상태와 HTTPS 응답을 확인한다.

`runs/duru-deployment.json`은 0600 권한의 로컬 운영 상태이며 요청 헤더와 기존 CloudFront 설정을 포함한다. Git에 넣거나 내용을 출력하지 않는다. 같은 체크아웃에서 보존한다. 서버에는 `/opt/duru/origin.env`와 원래 Caddy 설정 `/opt/duru/original.Caddyfile`을 보관한다. 운영 상태를 삭제해서 초기화하거나 키를 프런트 환경변수로 전달하지 않는다.

## 복구·운영 경계

수동 복구는 새 두루 컨테이너를 중지한 뒤 `duru-rollback`을 `duru-frontend`로 이름 변경·기동한다. 초기 공개 경로 자체를 되돌릴 때는 저장한 CloudFront 설정과 Caddy 원본을 사용하고, 기존 예선 서비스·터널을 중지하지 않는다. 예선 웹 컨테이너를 재생성하면 새 컨테이너를 `duru-edge`에 다시 연결해야 한다.

AWS의 기존 `bio3-stop.timer`는 2026-10-28 00:12 KST에 서버를 중지한다. 타이머를 변경하지 않았으며 서버 중지 후 두루도 접속되지 않는다. 운영 기간 연장은 별도 운영 결정이다.

포트 추가 조사 중 생성한 보안 그룹 `sg-06d78c025b58a30a0`은 ingress가 없고 인스턴스에 연결되지 않았다. 현재 계정의 삭제 권한이 없어 관리자 정리가 남았다. 실제 배포는 해당 그룹을 사용하지 않는다.
