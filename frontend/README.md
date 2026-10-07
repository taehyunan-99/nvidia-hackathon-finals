# 두루(Duru) 프런트

[공개 사이트](https://d25wpps17lj0dn.cloudfront.net/)는 실제 OpenShell 가족 에이전트에 연결된다. 합성 실행·테스트 모드 진입점은 제거했다. 서울 공개 sample 5건의 범위이며 전체 검색·잔여석·예약 가능성을 보장하지 않는다.

## 실행

Node.js 22.18+에서 저장소 전체를 checkout하고 `frontend/`에서 실행한다.

```sh
npm ci
npm run dev
npm run build
npm test
```

개발 주소는 http://127.0.0.1:5173 이다. `/api/runs`는 운영자 포워딩으로 연결된 로컬 8000번 API에 전달한다. [API 실행·소유권·재개](../agent/README.md#웹-연결)를 따른다. 연결 실패를 합성 결과로 대체하지 않는다.

## 흐름과 데이터

관심 분야 → 자녀별 학년·만 나이·인원·가족 구성 완료·보호자·운영 형태 → 날짜·지역 → 실제 분석 → 추가 조건 질문 또는 후보·근거·지도. 날짜 미정과 조건 부족은 확인 필요로 유지한다. 조건 수정은 이전 실행을 취소하고 입력을 유지한다. 같은 탭의 입력은 sessionStorage에 보관하며 결과는 새로고침 후 복원하지 않는다.

실행 중에는 2초마다 관측 이벤트를 받아 기존 분석 화면의 도구 상태와 기록을 갱신한다. 합성 재생과 실행되지 않은 스킬 표시는 제공하지 않는다. 모델·조회·독립 검증의 실제 이벤트만 표시한다. 모델 이벤트는 OpenShell 정책 집행 증거를 대신하지 않는다. 공개 자료에 좌표가 있는 후보만 지도에 표시하고, 지도 오류 시 후보·근거를 유지하며 다시 연결할 수 있다. 공식 신청 안내는 외부 페이지를 여는 링크이며 자동 예약은 수행하지 않는다.

## 네이버 지도

`frontend/.env.local`의 `NAVER_MAP_CLIENT_ID`를 로컬 설정 API 또는 배포 컨테이너 환경으로 전달한다. SDK가 요구하는 도메인 제한 Client ID만 `/api/maps-config`가 반환하며 Client Secret은 브라우저·이미지·Git에 넣지 않는다. 새 Maps의 Dynamic Map을 선택하고 `http://127.0.0.1`, `http://localhost`, `https://d25wpps17lj0dn.cloudfront.net`을 Web 서비스 URL 목록에 추가한 뒤 저장한다. SDK는 `ncpKeyId`를 사용한다.

## 배포와 검사

[Docker·AWS 수동 배포와 복구](../docs/playbooks/frontend-deployment.md)를 따른다. Docker는 같은 실제 프런트를 빌드하며 VITE_AGENT_MODE 설정으로 합성 실행을 선택할 수 없다. 타입 검사·9개 단위 검사와 공개 사이트의 대표 실제 왕복을 확인했다. 이전 합성 화면용 전체 브라우저 검사는 현재 제품 모드에 맞게 재작성하지 않았으며 이번 배포에서는 실행하지 않았다.
