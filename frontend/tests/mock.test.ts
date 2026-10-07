import test from "node:test";
import assert from "node:assert/strict";
import { buildMockRun } from "../src/mock.ts";
import { initialConditions, type Conditions } from "../src/contract.ts";
const full: Conditions = {
  interests: ["history", "craft"],
  grades: ["2"],
  guardians: "1",
  date: "2026-10-10",
  district: "all",
};
test("confirmed candidates have matching conditions and linked evidence", () => {
  const run = buildMockRun(full);
  assert.equal(run.candidates.length, 2);
  assert.equal(run.status, "completed");
  for (const c of run.candidates)
    for (const check of c.checks) {
      assert.equal(check.verdict, "pass");
      assert.ok(c.evidence.some((e) => e.id === check.evidenceId));
    }
});
test("missing family conditions prompt once, then remain unknown when skipped", () => {
  const input = { ...initialConditions, interests: full.interests };
  assert.equal(buildMockRun(input).outcome, "question");
  const run = buildMockRun(input, "normal", true);
  assert.equal(run.status, "partial");
  assert.equal(run.candidates.length, 2);
  assert.ok(
    run.candidates.every((c) => c.checks.every((x) => x.verdict === "unknown")),
  );
});
test("all children must qualify, and guardian absence excludes candidates", () => {
  assert.equal(
    buildMockRun({ ...full, grades: ["2", "preschool"] }).outcome,
    "empty",
  );
  assert.equal(buildMockRun({ ...full, guardians: "0" }).outcome, "empty");
});
test("date and region changes create fresh results without mutating earlier input", () => {
  const first = buildMockRun(full),
    changed = buildMockRun({ ...full, date: "2026-10-11" });
  assert.notEqual(first.run_id, changed.run_id);
  assert.equal(first.candidates.length, 2);
  assert.deepEqual(
    changed.candidates.map((c) => c.id),
    ["demo-craft"],
  );
  assert.equal(
    buildMockRun({ ...full, district: "jung" }).candidates.length,
    0,
  );
  assert.equal(first.conditions.date, "2026-10-10");
});
test("conflict preserves uncertainty and request failures are not empty searches", () => {
  const conflict = buildMockRun(full, "conflict");
  assert.equal(conflict.status, "partial");
  assert.equal(conflict.candidates[0].checks[0].verdict, "unknown");
  assert.equal(conflict.candidates[1].verdict, "pass");
  for (const scenario of ["failure", "policy"] as const) {
    const run = buildMockRun(full, scenario);
    assert.equal(run.outcome, "failed");
    assert.equal(run.status, "failed");
    assert.equal(run.candidates.length, 0);
  }
  assert.equal(buildMockRun(full, "empty").outcome, "empty");
});
test("budget termination retains only verified scope and no future evidence is referenced", () => {
  const run = buildMockRun(full, "budget");
  assert.equal(run.outcome, "limited");
  assert.equal(run.candidates.length, 1);
  const ids = new Set(
    run.candidates.flatMap((c) => c.evidence.map((e) => e.id)),
  );
  assert.ok(run.events.every((e) => e.evidence_ids.every((id) => ids.has(id))));
  assert.deepEqual(
    run.events.map((e) => e.seq),
    run.events.map((_, i) => i + 1),
  );
});
test("empty interest cannot start a run", () =>
  assert.throws(() => buildMockRun(initialConditions)));
