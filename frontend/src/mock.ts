import {
  type Candidate,
  type Conditions,
  type Run,
  type Scenario,
  type AssessedCandidate,
  type Observation,
  interestLabels,
} from "./contract.ts";
const fixtures: Candidate[] = [
  {
    id: "demo-history",
    title: "옛 서울의 이야기를 걷다",
    interest: "history",
    district: "jongno",
    experience:
      "옛 지도와 오늘의 거리를 비교하고 가족만의 역사 지도를 만드는 체험입니다.",
    place: "서울 종로구 · 예시 역사교육관",
    testCoordinates: { latitude: 37.5788, longitude: 126.9770 },
    dates: ["2026-10-10", "2026-10-17"],
    time: "10:00–11:30",
    grades: ["1", "2", "3", "4", "5", "6", "teen"],
    guardianRequired: true,
    cost: "가족당 10,000원 · 예시",
    preparation: "편한 신발, 필기도구",
    evidence: [],
  },
  {
    id: "demo-craft",
    title: "우리 가족의 작은 공방",
    interest: "craft",
    district: "jongno",
    experience:
      "전통 문양을 살펴보고 한지와 나무로 가족의 소품을 함께 만듭니다.",
    place: "서울 종로구 · 예시 전통공방",
    testCoordinates: { latitude: 37.5741, longitude: 126.9852 },
    dates: ["2026-10-10", "2026-10-11", "2026-10-17"],
    time: "14:00–15:30",
    grades: ["1", "2", "3", "4", "5", "6"],
    guardianRequired: true,
    cost: "1인 5,000원 · 예시",
    preparation: "작업하기 편한 옷",
    evidence: [],
  },
  {
    id: "demo-music",
    title: "처음 만나는 우리 장단",
    interest: "performance",
    district: "jung",
    experience:
      "국악기의 소리를 듣고 장구 장단을 따라 연주하며 우리 음악을 알아봅니다.",
    place: "서울 중구 · 예시 문화교육실",
    testCoordinates: { latitude: 37.5663, longitude: 126.9977 },
    dates: ["2026-10-11", "2026-10-18"],
    time: "11:00–12:00",
    grades: ["preschool", "1", "2", "3", "4", "5", "6", "teen"],
    guardianRequired: true,
    cost: "무료 · 예시",
    preparation: "별도 준비물 없음",
    evidence: [],
  },
];
export function buildMockRun(
  conditions: Conditions,
  scenario: Scenario = "normal",
  skipQuestion = false,
): Run {
  if (!conditions.interests.length)
    throw new Error("관심 분야를 하나 이상 선택해 주세요.");
  const run: Run = {
    run_id: crypto.randomUUID(),
    mode: "mock",
    conditions: structuredClone(conditions),
    scenario,
    status: "completed",
    outcome: "results",
    question: null,
    events: [],
    candidates: [],
    excluded: [],
    next_action: "후보의 조건과 예시 근거를 비교하거나 조건을 바꿔 보세요.",
  };
  const add = (
    kind: Observation["kind"],
    label: string,
    reason: string,
    status: Observation["status"],
    tool?: string,
    evidence_ids: string[] = [],
  ) =>
    run.events.push({
      seq: run.events.length + 1,
      kind,
      label,
      reason,
      status,
      tool,
      evidence_ids,
      ...(kind === "tool" ? { attempt: 1 } : {}),
    });
  add(
    "decision",
    "관심 분야에 맞는 후보 찾기",
    "예시 규칙: 선택한 관심 분야와 지역으로 후보 조회를 선택합니다.",
    "completed",
    "search",
  );
  add(
    "tool",
    "후보 조회 중",
    "합성 후보 목록을 조회하는 예시 단계입니다. 외부 API는 호출하지 않습니다.",
    "running",
    "search",
  );
  if (scenario === "failure" || scenario === "policy") {
    add(
      "tool",
      scenario === "policy"
        ? "조회 요청이 정책으로 거부된 예시"
        : "자료 조회에 실패한 예시",
      scenario === "policy"
        ? "미승인 목적지 요청을 차단한 가상 이벤트입니다. 실제 OpenShell 차단 검증은 미수행입니다."
        : "예시 API 응답 오류입니다. 후보가 없다는 뜻은 아닙니다.",
      "failed",
      "search",
    );
    run.status = "failed";
    run.outcome = "failed";
    run.next_action =
      scenario === "policy"
        ? "허용된 자료 경로를 운영자가 확인해야 합니다. 같은 차단 요청을 자동 재시도하지 않습니다."
        : "조건을 유지한 채 예시를 다시 실행할 수 있습니다.";
    add("result", "조회 미완료", run.next_action, "failed");
    return run;
  }
  const found =
    scenario === "empty"
      ? []
      : fixtures.filter(
          (c) =>
            conditions.interests.includes(c.interest) &&
            (conditions.district === "all" ||
              c.district === conditions.district),
        );
  add(
    "tool",
    `예시 후보 ${found.length}개 확인`,
    "조회된 범위의 결과입니다. 실제 서울 체험 공급량을 나타내지 않습니다.",
    "completed",
    "search",
  );
  if (found.length && !conditions.grades.length && !skipQuestion) {
    run.status = "partial";
    run.outcome = "question";
    run.question = "grades";
    run.next_action = "자녀의 학년을 선택하거나 미정인 채로 탐색을 계속하세요.";
    add(
      "decision",
      "참여 연령을 먼저 확인할까요?",
      "후보마다 참여 가능한 학년이 다릅니다. 사용자 조건을 추정하지 않고 선택 카드로 확인합니다.",
      "hold",
    );
    return run;
  }
  if (found.length) {
    add(
      "decision",
      "상세 참여조건 확인",
      "예시 규칙: 후보 요약만으로 동반자·운영 회차를 확정할 수 없어 상세 자료를 확인합니다.",
      "completed",
      "detail",
    );
    add(
      "tool",
      "상세 근거 조회 중",
      "예시 안내문의 참여조건과 운영일을 읽는 단계입니다.",
      "running",
      "detail",
    );
  }
  for (const [index, candidate] of found.entries()) {
    if (scenario === "budget" && index > 0) break;
    const failures = [
      conditions.grades.some((g) => !candidate.grades.includes(g))
        ? "선택한 자녀 학년 중 참여 대상이 아닌 학년이 있습니다."
        : "",
      conditions.guardians === "0" && candidate.guardianRequired
        ? "보호자 동반이 필요한 체험입니다."
        : "",
      conditions.date && !candidate.dates.includes(conditions.date)
        ? "선택한 날짜에 운영하는 예시 회차가 없습니다."
        : "",
    ].filter(Boolean);
    if (failures.length) {
      run.excluded.push({
        id: candidate.id,
        title: candidate.title,
        reason: failures.join(" "),
      });
      continue;
    }
    const conflict = scenario === "conflict" && index === 0;
    const evidenceId = `${candidate.id}-conditions`;
    const checks: AssessedCandidate["checks"] = [
      {
        label: "자녀 조건",
        verdict: conditions.grades.length && !conflict ? "pass" : "unknown",
        detail: conflict
          ? "예시 요약은 가족 대상, 상세는 초등 대상: 적용 대상 추가 확인 필요"
          : conditions.grades.length
            ? "선택한 모든 학년이 예시 참여 대상에 포함"
            : "자녀 학년 미입력",
        evidenceId,
      },
      {
        label: "보호자 동반",
        verdict: conditions.guardians === "unknown" ? "unknown" : "pass",
        detail:
          conditions.guardians === "unknown"
            ? "동반 여부 미정"
            : "보호자 동반 조건 확인",
        evidenceId,
      },
      {
        label: "운영 날짜",
        verdict: conditions.date ? "pass" : "unknown",
        detail: conditions.date
          ? `${conditions.date} 예시 운영 회차 확인`
          : "희망 날짜 미정 · 참여 가능일 확정 전",
        evidenceId,
      },
    ];
    run.candidates.push({
      ...candidate,
      checks,
      verdict: checks.some((c) => c.verdict === "unknown") ? "unknown" : "pass",
      reason: `${interestLabels[candidate.interest]}에 관심 있는 가족이 ${candidate.interest === "history" ? "이야기와 장소를 연결" : candidate.interest === "craft" ? "직접 만들며 전통 문양을 경험" : "소리와 연주로 전통을 경험"}할 수 있는 예시입니다.`,
      evidence: [
        {
          id: evidenceId,
          title: "참여조건 안내 · 합성 자료",
          source: "화면 검증용 fixture · 외부 조회 시점 없음",
          quote: `대상: ${candidate.grades.includes("preschool") ? "미취학부터" : "초등학생부터"} ${candidate.grades.includes("teen") ? "중·고등학생까지" : "초등 6학년까지"}, 보호자 동반. 운영일: ${candidate.dates.join(", ")}. ${conflict ? "요약과 상세의 대상 표현이 달라 확인이 필요합니다." : ""}`,
        },
      ],
    });
  }
  const ids = run.candidates.flatMap((c) => c.evidence.map((e) => e.id));
  if (found.length) {
    add(
      "tool",
      "상세 자료 확인",
      `비교 후보 ${run.candidates.length}개, 조건 불일치 ${run.excluded.length}개를 구분했습니다.`,
      "completed",
      "detail",
      ids,
    );
    if (scenario === "conflict")
      add(
        "validation",
        "자료 표현 충돌 발견",
        "대상 표현이 다른 예시 자료를 발견했습니다. 확인되지 않은 조건은 통과시키지 않습니다.",
        "hold",
        undefined,
        ids,
      );
    add(
      "decision",
      "조건과 출처 연결 검증",
      "예시 규칙: 날짜·학년·보호자 조건과 근거 식별자를 코드로 대조합니다.",
      "completed",
      "validate",
    );
    add(
      "tool",
      "조건 검증 중",
      "미입력·근거 충돌은 미확인으로 유지합니다.",
      "running",
      "validate",
    );
    add(
      "tool",
      "조건 검증 응답",
      "출처 없는 확정 추천이나 미확인 조건의 통과 여부를 확인했습니다.",
      "completed",
      "validate",
      ids,
    );
  }
  if (scenario === "budget" && found.length) {
    run.status = "partial";
    run.outcome = "limited";
    run.next_action =
      "실행 한도 종료 예시입니다. 확인한 후보만 보존하며 나머지 조회 여부는 미확인입니다.";
  } else if (!run.candidates.length) {
    run.outcome = "empty";
    run.next_action =
      "선택한 조건에 맞는 예시 후보가 없습니다. 날짜·분야·지역을 직접 수정해 보세요.";
  } else if (run.candidates.some((c) => c.verdict === "unknown")) {
    run.status = "partial";
    run.next_action =
      "미확인 조건을 살펴보고 조건을 보완하세요. 예시 후보의 실제 참여 가능성은 보장하지 않습니다.";
  }
  add(
    "validation",
    "결과 형식·근거 검증",
    run.status === "partial"
      ? "확인된 내용과 남은 확인을 분리했습니다."
      : "현재 예시 입력에 대한 결과와 근거 연결을 확인했습니다.",
    run.status === "partial" ? "hold" : "completed",
    undefined,
    ids,
  );
  add(
    "result",
    run.outcome === "empty"
      ? "조건에 맞는 예시 후보 없음"
      : run.status === "partial"
        ? "확인 필요 사항과 함께 결과 제시"
        : "예시 후보 비교 준비 완료",
    run.next_action,
    run.status === "partial" ? "hold" : "completed",
    undefined,
    ids,
  );
  return run;
}
