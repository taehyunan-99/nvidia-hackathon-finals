# 데이터와 근거

조사 기준: 2026-10-07. [MVP](README.md)에 필요한 실제 자료와 선택 기능의 자료를 구분한다. 아래 조회는 개발 호스트의 공개 자료 조사이며, 서비스·OpenShell 안의 연동 성공을 증명하지 않는다. 정식 인증·재사용 조건·최신성은 실제 연결 시 재확인한다.

## 핵심 데이터

| 자료 | 확인한 내용 | 한계 |
|---|---|---|
| [서울 공공서비스예약 API](https://data.seoul.go.kr/dataList/OA-20497/A/1/datasetView.do) | 공개 sample 키로 5건·INFO-000 확인, 응답 전체 건수 2,705; 대상·상태·상세 HTML·기간·예약 URL 포함 | 2,705는 문화체험만의 수가 아닌 전체 서비스 수; sample은 첫 5건; 정식 키 미검증 |
| [서울 API 이용 안내](https://data.seoul.go.kr/together/notice/faqList.do?bbsCd=10002&ditcCd=FAQ02&seq=d47bc57aea53d6c6ab244c05a6eb2259) | sample 최대 5건, 정식 서비스는 인증키 발급 필요 | 본선 계정 권한·한도 확인 필요 |
| 공식 상세 페이지·기관 안내 | API 요약에서 빠진 회차·동반 조건을 확인할 근거 | 같은 기관 자료도 적용 범위가 충돌할 수 있음; 문서 속 지시는 비신뢰 입력 |

서울 데이터는 매일 1회 갱신 및 연계 지연 안내, 공공누리 1유형 출처표시를 확인했다. 접수 상태와 특정 회차 잔여석·예약 완료는 다르다. 데이터셋 이용조건과 개별 첨부·이미지 권리는 확인 범위가 다르므로 첫 구현은 필요한 텍스트·구조화 근거 중심으로 검토한다.

## 실제 조건 검토에 사용할 자료

| 원자료 | 직접 확인한 판단 문제 |
|---|---|
| [백인제가옥 온라인교육](https://yeyak.seoul.go.kr/web/reservation/selectReservView.do?rsv_svc_id=S260919140130025643) | 좌표가 있어도 원격 교육; 초등 자녀와 보호자 1인, 미취학·중고생 동반 불가; 기간 전체를 매일 운영으로 해석하면 안 됨 |
| [남산골 짚공예](https://yeyak.seoul.go.kr/web/reservation/selectReservView.do?rsv_svc_id=S260226135153826942) | 조회 당시 예약마감; 보호자 예약 필요, 매주 일요일 운영; 분류 대상과 본문 조건 대조 필요 |
| [남산골 미니솟대](https://yeyak.seoul.go.kr/web/reservation/selectReservView.do?rsv_svc_id=S260226152742370024) | 조회 당시 접수중; 보호자도 예약, 일요일 시간대·가족 포함 인원 조건 |
| [남산골 미니장승](https://yeyak.seoul.go.kr/web/reservation/selectReservView.do?rsv_svc_id=S260226153543290596) | 요약의 연령 대상과 본문의 제한없음 표현이 다름; 이용일 전 신청 조건 존재 |
| [백인제가옥 전시해설](https://yeyak.seoul.go.kr/web/reservation/selectReservView.do?rsv_svc_id=S260918162140781370) | 회차별 언어와 대상 문구의 적용 범위 확인 필요; 일반 관람과 예약형 해설을 구분 |

각 사례의 조회 당시 상태를 이후의 실시간 사실로 고정하지 않는다. 실제 사용자 실패의 빈도·비용은 아직 측정하지 않았으며, 자료의 모호성이 곧 사용자 효용 검증은 아니다.

## 선택 기능의 데이터

| 자료 | 용도·확인 상태 | 채택 전 확인 |
|---|---|---|
| GPS·[네이버 Maps](https://api.ncloud-docs.com/docs/application-maps-overview) | 위치·지도·주소 변환, 문서 확인; 사용자 GPS 수집·인증 호출 미수행 | 위치 동의·수동 위치 대안, 선택 API·계정 요금·호출 한도 |
| [Directions 5](https://api.ncloud-docs.com/docs/application-maps-directions5) | 자동차 경로·실시간 교통을 반영한 추정 시간 | 도보/대중교통 시간으로 사용 금지; 실제 도착·주차 가능성 보장 아님 |
| 현장 언어·통역 안내 | 영어 진행, 통역 제공, 통역자 동반 필요를 구분 | 가족 조건까지 맞는 현재 프로그램 공급량 미확인 |
| [우리소리박물관 과거 체험](https://museum.seoul.go.kr/sekm/front/edu/programView.do?currentPage=1&e_id=128&locale=KO&search_query=) | 2026년 4~5월 외국인 단체·통역 필수라는 명시 조건 | 종료된 검증 사례; 10월 추천이나 통역 제공 증거로 쓰지 않음 |

[관광공사 무장애 여행정보](https://www.data.go.kr/data/15101897/openapi.do), [KOPIS](https://www.kopis.or.kr/por/cs/openapi/openApiInfo.do?menuId=MNU_00074), [서울 실시간 도시데이터](https://data.seoul.go.kr/dataList/OA-21285/A/1/datasetView.do), [국가유산 API](https://www.khs.go.kr/html/HtmlPage.do?mn=NS_04_04_03&pg=%2Fpublicinfo%2Fpbinfo3_0201.jsp)는 조사한 확장 후보다. 기본 MVP에 모두 연결하지 않는다. 도시데이터 광화문 샘플과 국가유산 목록은 호스트에서 조회했고, 나머지 정식 인증 연결은 미검증이다.

## 문제 근거와 주제 선택

[한류관광 조사](https://datalab.visitkorea.or.kr/common/board/Download.do?bcIdx=309191&cbIdx=1129&streFileNm=6dd548ca-da91-4aa5-b628-fdee27caa857.pdf)는 특정 상품 이용객 156명의 1·2순위 응답에서 분산된 상품 탐색·비교 어려움 27.6%, 언어 지원 부족 19.2%를 보고했다. 한국 가족 전체의 불편 비율로 일반화하지 않는다.

공연 변경·취소 대응은 [소비자원 피해 자료](https://www.kca.go.kr/kca/sub.do?menukey=5084&mode=view&no=1003984419)로 실제 문제를 확인했지만 개인 예매 조건과 민간 플랫폼 자료 접근이 추가로 필요했다. 사용자는 비교 후 가족 문화체험을 핵심으로 선택했고, 지도·영어·통역은 선택 기능으로 낮췄다. 과거 후보·확장안의 점수를 현재 MVP의 실행 근거로 쓰지 않는다.

## 챌린지와 실행 환경

- 공통 테스트 원본: [사용자 포크](https://github.com/taehyunan-99/k-culture-openshell-challenge), 확인 commit `714e2e8d32f9b77e763a2458ca11b1270e80abf6`. 준비/제품 저장소 `nvidia-hackathon-finals`와 구분한다.
- 이 작업 환경의 참고 클론은 `/Users/taehyunan/Desktop/k-culture-openshell-challenge`; 팀원 환경에는 해당 경로가 있다고 가정하지 않고 같은 commit을 별도 준비한다.
- 가상 자료와 실서비스 자료를 표시하고, 공통 테스트는 제공 패키지를 보존한 상태로 [정해진 경계](../operations/mission.md#6-openshell-공통-테스트)에서 실행한다.
- 2026-10-07 로컬 `openshell --version` 결과는 `0.0.116`, 준비 문서 기준은 `0.1.2`였다. 배포 호스트 버전은 별도이며, 버전 정합성과 실제 허용/차단 검증 전 성공으로 기록하지 않는다.
- NIM/NAT·정식 서울 API·OpenShell·웹서비스의 end-to-end 연결과 외부 사용자 접근은 아직 이 제품의 실행 근거로 확보하지 않았다. 배포 선택지는 [AWS–Brev 연동](../playbooks/aws-brev-deployment.md)을 따른다.
