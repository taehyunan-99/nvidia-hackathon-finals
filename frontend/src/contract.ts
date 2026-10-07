// Frontend-only proposal. Reconcile with the agent producer before live integration.
export type Interest = "history" | "craft" | "performance";
export type Grade = "preschool" | "1" | "2" | "3" | "4" | "5" | "6" | "teen";
export interface Conditions {
  interests: Interest[];
  grades: Grade[];
  guardians: "unknown" | "0" | "1" | "2+";
  date: string | null;
  district: "all" | "jongno" | "jung";
}
export type Scenario =
  "normal" | "conflict" | "empty" | "failure" | "policy" | "budget";
export type State = "empty" | "running" | "completed" | "hold" | "failed";
export interface Observation {
  seq: number;
  kind: "decision" | "tool" | "validation" | "result";
  label: string;
  reason: string;
  status: State;
  evidence_ids: string[];
  tool?: string;
  attempt?: number;
  error_code?: string;
}
export interface Evidence {
  id: string;
  title: string;
  quote: string;
  source: string;
}
export interface Check {
  label: string;
  verdict: "pass" | "unknown";
  detail: string;
  evidenceId: string;
}
export interface Candidate {
  id: string;
  title: string;
  interest: Interest;
  district: "jongno" | "jung";
  experience: string;
  place: string;
  testCoordinates?: { latitude: number; longitude: number };
  dates: string[];
  time: string;
  grades: Grade[];
  guardianRequired: boolean;
  cost: string;
  preparation: string;
  evidence: Evidence[];
}
export interface AssessedCandidate extends Candidate {
  checks: Check[];
  verdict: "pass" | "unknown";
  reason: string;
}
export interface Run {
  run_id: string;
  mode: "mock";
  conditions: Conditions;
  scenario: Scenario;
  status: "completed" | "partial" | "failed";
  outcome: "results" | "empty" | "question" | "failed" | "limited";
  question: "grades" | null;
  events: Observation[];
  candidates: AssessedCandidate[];
  excluded: { id: string; title: string; reason: string }[];
  next_action: string;
}
export const interestLabels: Record<Interest, string> = {
  history: "역사 탐방",
  craft: "전통 공예",
  performance: "전통 공연",
};
export const gradeLabels: Record<Grade, string> = {
  preschool: "미취학",
  "1": "초등 1학년",
  "2": "초등 2학년",
  "3": "초등 3학년",
  "4": "초등 4학년",
  "5": "초등 5학년",
  "6": "초등 6학년",
  teen: "중·고등학생",
};
export const initialConditions: Conditions = {
  interests: [],
  grades: [],
  guardians: "unknown",
  date: null,
  district: "all",
};
export const tools = {
  search: "후보 조회",
  detail: "상세 근거 조회",
  validate: "조건 검증",
};
export function summarize(c: Conditions) {
  return [
    c.interests.map((x) => interestLabels[x]).join(" · ") || "관심 분야 미선택",
    c.grades.map((x) => gradeLabels[x]).join(" · ") || "자녀 조건 미정",
    c.guardians === "unknown"
      ? "보호자 미정"
      : `보호자 ${c.guardians === "2+" ? "2명 이상" : c.guardians + "명"}`,
    c.date || "날짜 미정",
    c.district === "all"
      ? "서울 전체"
      : c.district === "jongno"
        ? "종로구"
        : "중구",
  ];
}
