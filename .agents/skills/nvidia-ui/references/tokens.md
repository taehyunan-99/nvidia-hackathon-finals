# 토큰과 참고 출처

확정값·이유·적용 조건의 원본은 [design-decisions.json](../../../../docs/design/design-decisions.json), 실행 토큰은 [tokens.css](../assets/tokens.css)다. 아래 출처는 비교 근거이며 확정값을 대체하지 않는다.

Bio-3 `frontend/src/nvidia-theme.css`와 `docs/frontend-hosting/design-guide.md`를 2026-10-03 검토해 일반화했다. 원본 commit: `52f6be29e432b1fa660e2a9b3b6b7556d04793d4`.

- 강조 #76B900 + 검은 버튼 글자, 밝은 중립 배경, 얇은 border, 사각 CTA.
- 작은 녹색 텍스트는 #426700, dark에서는 #A2D45B. 녹색 배경 위 흰 작은 글자를 기본으로 쓰지 않는다.
- 4px 간격 체계. 간격 8/12/16/24/32/48/64, 기본 panel 24, 페이지 32. 모두 비교를 위한 초기 후보값이다.
- 본문 16px, 보조 13px, 제목 22/28/36, 발표 48. 한국어 행간 1.6. 모바일용 글자 크기 조정은 이번 범위에서 제외한다.
- 한글 SUIT Variable가 실제 제공되면 사용하고 없으면 시스템 sans-serif. 영어 Arial/Helvetica. 외부 폰트가 없어도 읽을 수 있어야 한다.
- 기본 light, dark는 선택. 모서리 0, 그림자는 기본 없음. 사용자 선택으로 토큰을 바꿀 수 있다.

이는 예선 프로젝트의 선택을 재사용한 값이다. [NVIDIA 홈페이지](https://www.nvidia.com/ko-kr/)의 9월 25일 관찰에 근거하며 지금 모든 NVIDIA 제품에 강제되는 규칙이 아니다. [Elements](https://nvidia.github.io/elements/)는 별도의 작업 UI 시스템이며 상호작용 참고로만 쓴다. 공식 폰트/로고/배너 자산은 복제하지 않는다.

헤더와 브랜딩의 크기는 실제 서비스의 사용자 과업을 기준으로 비교한다. 입력·결과 확인을 방해할 정도로 높이를 차지하지 않게 한다. 상태는 색과 문구/아이콘을 함께 쓴다.

## 비활성 보조 버튼 참고 근거

2026-10-04 확인. 다음은 참고 구현이며 사용자의 디자인 확정값이 아니다.

- NVIDIA 공식 공통 CSS의 `.nv-button-transparent .nv-button-disabled .btn-content`: 배경 transparent, 테두리 rgba(153,153,153,0.5), 글자 #999999. 흰 카드 위에서는 배경이 흰색으로 보이고 테두리는 #cccccc로 합성된다. [공식 CSS](https://www.nvidia.com/etc.clientlibs/nvidiaweb/clientlibs/clientlib-site.min.4bc41d6211db48d6007515e960b1001b.css)
- 예선 commit 52f6be29e432b1fa660e2a9b3b6b7556d04793d4의 `style.css`: 일반 보조 버튼은 `--bg-secondary` 배경, `button:disabled`는 전체 opacity 0.5. `nvidia-theme.css`의 밝은 배경은 #ffffff라 흰 카드 위에서 배경은 흰색으로 유지되며 글자·테두리가 흐려진다. [예선 CSS](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/frontend/src/style.css) · [예선 테마](https://github.com/taehyunan-99/nvidia-hackathon/blob/52f6be29e432b1fa660e2a9b3b6b7556d04793d4/frontend/src/nvidia-theme.css)
- 사용자는 공식 사이트 느낌을 우선해 비활성 보조 버튼 배경을 transparent로 확정했다. 글자 색은 #999999, 테두리 색은 rgba(153,153,153,0.5)로 확정했다. 예선의 #111111 글자에 적용된 전체 opacity 0.5는 흰 바탕에서 #888888에 해당하며, 원본 CSS에 #888888을 지정한 것은 아니다.

예선의 일반 `.secondary` 테두리는 `--text-primary`(#111111)이며 비활성 opacity 0.5 적용 시 흰 바탕에서 #888888에 해당한다. `.review-add-row .secondary`는 `--agent-border`를 사용하므로 이 일반 테두리와 다르다. 비교 화면은 테두리 합성 효과만 재현하고 버튼 전체 opacity를 적용하지 않는다.

2026-10-04 전환 방식 확인: 공식 공통 CSS `.nv-button .btn-content`는 `background-color .2s ease-out`, 외곽선 버튼은 `border-color .2s ease-out`. 예선 `style.css`의 `button`은 `transition: background var(--duration-fast)`이고 `tokens.css`의 값은 0.15s라 기본 timing function ease가 적용된다. 본선의 두 버튼 전환 시간은 이미 120ms로 확정했으며 공식·예선 시간으로 덮어쓰지 않는다.

2026-10-04 입력창 배경 확인: 공식 공통 CSS의 `.navigation .search-outter-container .search-inner-container .search-form .search-box-input`는 background-color #fff. 이는 검색 입력창 사례이며 모든 폼의 규칙은 아니다. 예선 `agent-experience.css`의 `.review-form input:not([type="checkbox"])`는 `--bg-secondary`를 사용하고 밝은 테마에서 #ffffff다.

2026-10-04 입력 글자 색 확인: 같은 공식 `.search-box-input` 규칙의 color는 #414347이다. 예선 `.review-form input:not([type="checkbox"])`는 `--text-primary`를 사용하며 밝은 테마 값은 #111111이다. 공식 검색 입력창의 사례와 예선 일반 폼의 사례를 구분해 비교한다.

2026-10-04 placeholder 확인 경계: 공식 공통 clientlib-site CSS에서 placeholder 색 규칙을 확보하지 못했고 공식 페이지의 검색 조작 후 검색 입력창이 표시되지 않아 실제 placeholder 색도 미확인이다. 예선 frontend/src의 CSS에는 placeholder 전용 규칙이 없다. 원본에서 확인하지 못한 색은 브라우저 기본값을 추정해 공식값으로 기록하지 않는다. 현재 placeholder 비교 후보는 자체 제안이다.

2026-10-04 밝은 페이지 배경 확인: 공식 공통 CSS의 `.nv-container--card-light,.nv-container--theme-light,.nv-modalcontainer,.theme-light`는 background-color #fff. 예선 `style.css`의 body는 `--bg-primary`를 사용하고 `nvidia-theme.css`에서 #ffffff다. 예선 agent-shell의 그라데이션 및 양 사이트의 어두운 hero 등 특수 구역과 구분한다.

2026-10-04 카드 제목 색 확인: 공식 공통 CSS의 `.nv-container--card-light h1`~`h6`, `.theme-light` 계열 heading은 color #000. 예선 기본 h3는 body의 `--text-primary`를 상속하고 밝은 테마 값은 #111111이다. 특정 섹션의 별도 제목 스타일에는 일반화하지 않는다.

2026-10-04 카드 가로 간격 확인: 공식 공통 CSS `.nv-carousel .cmp-carousel__slides.fixed-width .cmp-carousel__item` 및 `.nv-carousel-home` 대응 규칙은 margin-right 30px, 마지막 항목은 0이다. 예선 `style.css`의 `.two-col`은 gap var(--space-6)=24px, `agent-experience.css`의 `.test-candidates`는 gap var(--space-4)=16px. 캐러셀·일반 패널·밀집 후보 목록은 용도가 다르므로 하나의 사이트 전역 간격으로 일반화하지 않는다.

2026-10-04 카드 세로 간격 확인: 공식 공통 CSS `.nv-spotify__card--list` 기본 규칙은 margin-bottom 60px이며 팟캐스트 콘텐츠 목록 사례다. 예선 `.agent-start > .analysis-launcher + .analysis-launcher`는 margin-top var(--space-8)=32px이며 연속 작업 패널 사례다. 공식 `.nv-usecase--card`의 margin-bottom 20px는 639px 이하 전용이므로 데스크톱 근거로 사용하지 않는다.

2026-10-04 한글 줄바꿈 확인: 공식 홈페이지 #ai-data-science-blade의 인공지능 소개 문단은 브라우저 계산 스타일 word-break:normal / overflow-wrap:normal이었다. 예선 agent-experience.css의 .test-scenario-summary는 word-break:keep-all이며 소개 페이지 제목·팀 설명 등에도 keep-all을 사용한다. 카드 비교에서는 긴 연속 문자열의 넘침 방지를 위해 양쪽에 overflow-wrap:anywhere를 추가하므로 두 사이트 전체 규칙을 그대로 복제한 것은 아니다.

2026-10-04 긴 기술 정보 확인: 공식 공통 CSS `.nv-table table.even-columns td, .nv-table table.even-columns th`는 overflow-wrap:anywhere. 예선 report-view.css의 `.report-file-info span, .report-file-info small`과 `.report-provenance dd`도 overflow-wrap:anywhere를 사용한다. 이는 공식 표 셀·예선 파일 정보의 사례이며 모든 제목·목록의 생략 정책으로 일반화하지 않는다.

2026-10-04 표 셀 여백 확인: 공식 nv-table thead th는 padding var(--thspacingTopBottom,22px) var(--thspacingLeftRight,1pc), tbody td/th는 var(--tbspacingTopBottom,22px) var(--tbspacingLeftRight,1pc)이다. 22px는 fallback이며 개별 페이지 변수로 달라질 수 있다. 예선 report-view.css의 .report-table th/td는 --space-4=16px를 사용한다. 공식 small-viewport 전용 8px 규칙은 데스크톱 근거에서 제외한다.

2026-10-04 표 본문 크기 확인: 공식 공통 CSS `.nv-table table`은 font-size 14px, line-height 1.2, font-variant-numeric tabular-nums. 예선 `.report-table`은 --text-caption=13px이며 tbody th만 --text-body=16px로 별도 지정한다. 이번 비교는 일반 tbody td의 크기만 다룬다.

2026-10-04 표 본문 굵기 확인: 공식 공통 CSS body는 font-weight:400이고 .nv-table 일반 td에는 별도 굵기 재정의가 없어 상속한다. 예선 style.css body의 font shorthand는 굵기를 생략해 normal(400)이며 report-table 일반 td도 상속한다. 공식 table th와 예선 thead th의 700은 본문 td 기본값과 구분한다.

2026-10-04 표 본문 줄 높이 확인: 공식 .nv-table table은 14px / line-height 1.2(16.8px). 예선 body는 --leading-body=1.6의 unitless 줄 높이이며 report-table 일반 td의 13px에서 20.8px에 해당한다. 비교에서는 확정한 14px로 통일해 1.6을 22.4px로 보여주므로 원본 예선의 픽셀 높이를 복제한 것은 아니다.

일반 열 헤더 크기 비교 근거: 앞서 확인한 공식 .nv-table table의 font-size 14px를 일반 thead th가 상속한다. 예선 .report-table의 --text-caption=13px를 thead th가 상속하며 굵기만 700으로 별도 지정한다. 공식 hcr 그룹 헤더나 예선 tbody th는 이 기본 열 헤더 사례와 구분한다.

표 열 헤더 줄 높이 비교는 앞서 확인한 공식 .nv-table table의 1.2와 예선 body의 unitless 1.6을 일반 thead th가 상속하는 기준을 사용한다. 공식 14px/1.2, 예선 13px/1.6이 원본이며 비교는 확정한 14px/700에서 비율만 바꾼다.

2026-10-04 표 헤더 배경 확인: 공식 밝은 .nv-table-wrapper는 --table-bg-color-1:#fff, --table-bg-color-2:#eee이며 table.default td/th와 table.alt-bg td/th가 각각 사용한다. 전체 셀에 적용되는 공식 테마와 이번 헤더 전용 비교를 구분한다. 예선 .report-table thead는 --agent-soft를 사용하고 agent-experience.css의 값은 #edf5e1이다.
