import { readConditions, saveConditions } from "./input-session";
import { layoutActivityLabels } from "./activity-layout";
import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  renderActivity,
  renderFlow,
} from "../../.agents/skills/nvidia-ui/assets/agent-flow.mjs";
import team from "../../.agents/skills/nvidia-ui/assets/team-content.json";
import {
  type Conditions,
  type Grade,
  type Interest,
  type Run,
  type Scenario,
  type State,
  interestLabels,
  gradeLabels,
  tools,
  summarize,
} from "./contract";
import { buildMockRun } from "./mock";
import { MapResults } from "./MapResults";

const mapPreview = import.meta.env.DEV && new URLSearchParams(location.search).get("mapDemo") === "1";
const mapPreviewRun = mapPreview ? buildMockRun({
  interests: ["history", "craft", "performance"], grades: ["3"],
  guardians: "1", date: null, district: "all",
}) : null;

// The shared JavaScript renderer infers its demo tool IDs too narrowly.
const drawActivity = renderActivity as unknown as (
  root: HTMLElement,
  run: Run,
  count: number,
  options: { tools: Record<string, string>; playing: boolean },
) => void;
const repository = "https://github.com/taehyunan-99/nvidia-hackathon-finals";
const dates = [
  ["2026-10-10", "10월 10일", "토요일"],
  ["2026-10-11", "10월 11일", "일요일"],
  ["2026-10-17", "10월 17일", "토요일"],
  ["2026-10-18", "10월 18일", "일요일"],
];
const scenarios: [Scenario, string][] = [
  ["normal", "일반 탐색"],
  ["conflict", "자료 충돌"],
  ["empty", "후보 없음"],
  ["failure", "조회 실패"],
  ["policy", "정책 거부"],
  ["budget", "실행 한도 종료"],
];
const icons: Record<State, string> = {
  empty: "○",
  running: "…",
  completed: "✓",
  hold: "!",
  failed: "×",
};
function Status({ state, children }: { state: State; children: ReactNode }) {
  return (
    <span className="nv-status" data-state={state}>
      {icons[state]} {children}
    </span>
  );
}
function Button({
  children,
  onClick,
  disabled,
  primary = false,
}: {
  children: ReactNode;
  onClick: () => void;
  disabled?: boolean;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      className={`nv-button ${primary ? "nv-primary" : "nv-secondary"}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
function Choice({
  selected,
  title,
  description,
  onClick,
  number,
}: {
  selected: boolean;
  title: string;
  description?: string;
  onClick: () => void;
  number?: string;
}) {
  return (
    <button
      type="button"
      className="choice"
      aria-pressed={selected}
      onClick={onClick}
    >
      {number && <span className="choice-number">{number}</span>}
      <span className="choice-text">
        <strong>{title}</strong>
        {description && <span>{description}</span>}
      </span>
      <span aria-hidden="true" className="choice-check">
        {selected ? "✓" : "+"}
      </span>
    </button>
  );
}
function toggle<T>(values: T[], value: T) {
  return values.includes(value)
    ? values.filter((x) => x !== value)
    : [...values, value];
}
function GradeChoices({
  value,
  onChange,
}: {
  value: Grade[];
  onChange: (v: Grade[]) => void;
}) {
  return (
    <div className="choices grades">
      {(Object.entries(gradeLabels) as [Grade, string][]).map(([id, label]) => (
        <Choice
          key={id}
          title={label}
          selected={value.includes(id)}
          onClick={() => onChange(toggle(value, id))}
        />
      ))}
      <Choice
        title="아직 미정"
        selected={!value.length}
        onClick={() => onChange([])}
      />
    </div>
  );
}
function Activity({
  run,
  count,
  playing,
  compact = false,
}: {
  run: Run;
  count: number;
  playing: boolean;
  compact?: boolean;
}) {
  const graph = useRef<HTMLDivElement>(null),
    flow = useRef<HTMLDivElement>(null);
  const [selected, setSelected] = useState(0);
  useEffect(() => {
    if (graph.current) {
      drawActivity(graph.current, run, count, { tools, playing });
      layoutActivityLabels(graph.current);
    }
    if (flow.current)
      renderFlow(flow.current, run, count, selected || count, (seq: number) =>
        setSelected(seq),
      );
  }, [run, count, selected, playing]);
  return (
    <>
      <div
        className={`activity-panel ${compact ? "activity-compact" : ""}`}
        ref={graph}
      />
      {!compact && (
        <details className="execution-details">
          <summary>
            도구 선택 이유와 단계별 기록 <span>{count}개 관측</span>
          </summary>
          <div ref={flow} />
        </details>
      )}
    </>
  );
}
function Team() {
  const [failed, setFailed] = useState<string[]>([]);
  return (
    <>
      <div className="page-heading">
        <p className="eyebrow">THE TEAM</p>
        <h1 tabIndex={-1}>함께 만드는 문화체험</h1>
        <p>가족의 관심이 함께하는 경험으로 이어지도록.</p>
      </div>
      <div className="nv-card-grid team-grid">
        {team.team.members.map((member, index) => (
          <article className="nv-card member" key={member.id}>
            <span className="eyebrow">0{index + 1} / TEAM MEMBER</span>
            <div className="avatar">
              <span aria-hidden="true">{member.name[0]}</span>
              {!failed.includes(member.id) ? (
                <img
                  src={member.avatar_url}
                  alt={member.name}
                  onError={() => setFailed((v) => [...v, member.id])}
                />
              ) : null}
            </div>
            <h2>{member.name}</h2>
            <p className="handle">{member.handle}</p>
            {member.role && <p>{member.role}</p>}
            {member.contribution && <p>{member.contribution}</p>}
            {member.profile_url && (
              <a
                href={member.profile_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                개인 GitHub
              </a>
            )}
          </article>
        ))}
      </div>
      <section className="repository-block">
        <div>
          <p className="eyebrow">OPEN PROJECT</p>
          <h2>프로젝트 코드와 개발 기록</h2>
          <p>서비스 구현과 실행 방법을 저장소에서 확인하세요.</p>
        </div>
        <a
          className="nv-button nv-secondary"
          href={repository}
          target="_blank"
          rel="noopener noreferrer"
        >
          GitHub에서 보기
        </a>
      </section>
    </>
  );
}
export default function App() {
  const [tab, setTab] = useState<"explore" | "team">("explore");
  const [screen, setScreen] = useState<
    "input" | "analysis" | "question" | "results"
  >(mapPreview ? "results" : "input");
  const [step, setStep] = useState(0);
  const [conditions, setConditions] = useState<Conditions>(readConditions);
  const [scenario, setScenario] = useState<Scenario>("normal");
  const [run, setRun] = useState<Run | null>(mapPreviewRun);
  const [count, setCount] = useState(mapPreviewRun?.events.length ?? 0),
    [playing, setPlaying] = useState(false);
  const [answer, setAnswer] = useState<Grade[]>([]),
    [compared, setCompared] = useState<string[]>([]);
  useEffect(() => {
    saveConditions(conditions);
  }, [conditions]);
  function goHome() {
    setTab("explore");
    setScreen("input");
    setStep(0);
    setPlaying(false);
  }
  function resume() {
    if (run)
      setScreen(
        ended
          ? run.outcome === "question"
            ? "question"
            : "results"
          : "analysis",
      );
  }
  const headingContainer = useRef<HTMLElement>(null);
  const ended = !!run && count >= run.events.length;
  useEffect(() => {
    headingContainer.current?.querySelector<HTMLElement>("h1")?.focus();
  }, [tab, screen, step]);
  useEffect(() => {
    if (!run || !playing || count >= run.events.length) return;
    const timer = window.setTimeout(() => setCount((v) => v + 1), 650);
    return () => window.clearTimeout(timer);
  }, [run, playing, count]);
  useEffect(() => {
    if (ended) {
      setPlaying(false);
      if (run?.outcome === "question") setScreen("question");
    }
  }, [ended, run]);
  const change = <K extends keyof Conditions>(key: K, value: Conditions[K]) =>
    setConditions((v) => ({ ...v, [key]: value }));
  function start(next = conditions, skipQuestion = false) {
    setConditions(next);
    setRun(buildMockRun(next, scenario, skipQuestion));
    setCount(0);
    setCompared([]);
    setAnswer([]);
    setPlaying(true);
    setScreen("analysis");
  }
  function edit() {
    setPlaying(false);
    setRun(null);
    setCount(0);
    setCompared([]);
    setScreen("input");
    setStep(0);
  }
  const state: State = !run
    ? "empty"
    : !ended
      ? "running"
      : run.status === "failed"
        ? "failed"
        : run.status === "partial"
          ? "hold"
          : "completed";
  const resultTitle = !run
    ? ""
    : run.outcome === "failed"
      ? "자료를 확인하지 못했어요"
      : run.outcome === "empty"
        ? "조건에 맞는 후보가 없어요"
        : run.outcome === "limited"
          ? "확인한 후보부터 살펴보세요"
          : run.status === "partial"
            ? "이런 체험은 어떠세요?"
            : "우리 가족이 함께할 문화체험";
  const summary = summarize(
    screen === "input" ? conditions : run?.conditions || conditions,
  );
  return (
    <div className="nv-ui app">
      <a className="skip-link" href="#main">
        본문으로 이동
      </a>
      <header className="site-header">
        <button className="brand" onClick={goHome} aria-label="두루 홈">
          <img className="brand-icon" src="/duru-icon.svg" alt="" />
          <span className="brand-name">
            두루 <small>Duru</small>
          </span>
        </button>
        <nav aria-label="주 메뉴">
          <button
            aria-current={tab === "explore" ? "page" : undefined}
            onClick={goHome}
          >
            체험 찾기
          </button>
          <button
            aria-current={tab === "team" ? "page" : undefined}
            onClick={() => setTab("team")}
          >
            팀원 소개
          </button>
          <a href={repository} target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </nav>
        {tab === "explore" && screen !== "input" && (
          <span className="mode-tag">MOCK · 예시 실행</span>
        )}
      </header>
      <div className="app-shell simple-shell">
        <main
          id="main"
          className={
            tab === "explore" && screen === "input"
              ? "start-screen"
              : screen === "analysis"
                ? "analysis-screen"
                : undefined
          }
          ref={headingContainer}
        >
          {tab === "team" ? (
            <Team />
          ) : (
            <>
              {screen !== "input" && (
                <ol className="top-steps" aria-label="탐색 단계">
                  {["조건 선택", "에이전트 분석", "결과 비교"].map(
                    (label, index) => (
                      <li
                        key={label}
                        aria-current={
                          (screen === "results" ? 2 : 1) === index
                            ? "step"
                            : undefined
                        }
                      >
                        <span>0{index + 1}</span>
                        {label}
                      </li>
                    ),
                  )}
                </ol>
              )}
              {screen === "input" && (
                <>
                  <div className="page-heading">
                    <h1 tabIndex={-1}>우리 가족의 다음 문화체험</h1>
                    <p>함께하고 싶은 경험을 두루 찾아보세요.</p>
                  </div>
                  {run && (
                    <div className="resume-action">
                      <Button onClick={resume}>이전 분석 보기</Button>
                    </div>
                  )}
                  <div className="input-layout">
                    <section className="input-section">
                      <div className="input-stepper" aria-label="입력 단계">
                        {["관심 분야", "가족 조건", "날짜와 지역"].map(
                          (label, index) => (
                            <button
                              key={label}
                              aria-current={step === index ? "step" : undefined}
                              disabled={
                                index > 0 && !conditions.interests.length
                              }
                              onClick={() => setStep(index)}
                            >
                              <span>0{index + 1}</span>
                              {label}
                            </button>
                          ),
                        )}
                      </div>
                      <div className="form-section">
                        <div className="section-heading">
                          <h2>
                            {
                              [
                                "어떤 문화에 관심이 있나요?",
                                "누구와 함께하나요?",
                                "언제, 어디서 경험할까요?",
                              ][step]
                            }
                          </h2>
                          <span>{step + 1} / 3</span>
                        </div>
                        <p className="nv-description">
                          {
                            [
                              "관심 있는 분야를 모두 골라 주세요.",
                              "자녀의 학년은 여러 개를 선택할 수 있어요. 아직 정하지 않아도 괜찮아요.",
                              "날짜가 미정이어도 후보를 살펴볼 수 있어요. 아래 날짜는 화면 체험용입니다.",
                            ][step]
                          }
                        </p>
                        <div className="nv-form-content">
                          {step === 0 && (
                            <div className="choices interests">
                              {(Object.keys(interestLabels) as Interest[]).map(
                                (id, index) => (
                                  <Choice
                                    key={id}
                                    number={`0${index + 1}`}
                                    title={interestLabels[id]}
                                    description={
                                      [
                                        "옛 이야기와 장소를 함께 발견하기",
                                        "손으로 만들며 전통을 경험하기",
                                        "우리 소리와 장단을 만나기",
                                      ][index]
                                    }
                                    selected={conditions.interests.includes(id)}
                                    onClick={() =>
                                      change(
                                        "interests",
                                        toggle(conditions.interests, id),
                                      )
                                    }
                                  />
                                ),
                              )}
                            </div>
                          )}
                          {step === 1 && (
                            <>
                              <fieldset>
                                <legend>함께하는 자녀의 학년</legend>
                                <GradeChoices
                                  value={conditions.grades}
                                  onChange={(v) => change("grades", v)}
                                />
                              </fieldset>
                              <fieldset>
                                <legend>함께하는 보호자</legend>
                                <div className="choices compact">
                                  {(["unknown", "0", "1", "2+"] as const).map(
                                    (id) => (
                                      <Choice
                                        key={id}
                                        title={
                                          id === "unknown"
                                            ? "아직 미정"
                                            : id === "0"
                                              ? "동반하지 않음"
                                              : id === "1"
                                                ? "1명"
                                                : "2명 이상"
                                        }
                                        selected={conditions.guardians === id}
                                        onClick={() => change("guardians", id)}
                                      />
                                    ),
                                  )}
                                </div>
                              </fieldset>
                            </>
                          )}
                          {step === 2 && (
                            <>
                              <fieldset>
                                <legend>희망 날짜 · 2026년 10월 예시</legend>
                                <div className="choices dates">
                                  <Choice
                                    title="아직 미정"
                                    description="후보부터 살펴볼게요"
                                    selected={!conditions.date}
                                    onClick={() => change("date", null)}
                                  />
                                  {dates.map(([id, title, day]) => (
                                    <Choice
                                      key={id}
                                      title={title}
                                      description={day}
                                      selected={conditions.date === id}
                                      onClick={() => change("date", id)}
                                    />
                                  ))}
                                </div>
                              </fieldset>
                              <fieldset>
                                <legend>관심 지역</legend>
                                <div className="choices compact">
                                  {(
                                    [
                                      ["all", "서울 전체"],
                                      ["jongno", "종로구"],
                                      ["jung", "중구"],
                                    ] as const
                                  ).map(([id, label]) => (
                                    <Choice
                                      key={id}
                                      title={label}
                                      selected={conditions.district === id}
                                      onClick={() => change("district", id)}
                                    />
                                  ))}
                                </div>
                              </fieldset>
                            </>
                          )}
                        </div>
                        <div className="nv-form-submit form-actions">
                          <span className="nv-description">
                            {step === 0
                              ? "관심 분야를 하나 이상 선택해 주세요."
                              : "미정인 조건은 결과에서 확인 필요로 표시해요."}
                          </span>
                          <div className="nv-actions">
                            {step > 0 && (
                              <Button onClick={() => setStep(step - 1)}>
                                이전
                              </Button>
                            )}
                            <Button
                              primary
                              disabled={!conditions.interests.length}
                              onClick={() =>
                                step < 2 ? setStep(step + 1) : start()
                              }
                            >
                              {step < 2 ? "다음" : "예시 체험 찾기"}
                            </Button>
                          </div>
                        </div>
                      </div>
                    </section>
                  </div>
                  {new URLSearchParams(window.location.search).get("demo") ===
                    "1" && (
                    <details className="demo-controls">
                      <summary>화면 검증용 예시 설정</summary>
                      <p>
                        외부 호출 없이 화면의 상태 전환을 확인합니다. 실제 추천
                        품질·정책 검증 결과가 아닙니다.
                      </p>
                      <div className="choices compact">
                        {scenarios.map(([id, label]) => (
                          <Choice
                            key={id}
                            title={label}
                            selected={scenario === id}
                            onClick={() => setScenario(id)}
                          />
                        ))}
                      </div>
                    </details>
                  )}
                </>
              )}
              {screen === "analysis" && run && (
                <>
                  <section className="analysis-box nv-card">
                    <h1 tabIndex={-1}>에이전트 분석</h1>
                    <div className="section-heading">
                      <p className="current-observation">
                        {run.events[count - 1]?.label || "분석 준비 중"}
                      </p>
                      <Status state={state}>
                        {!ended
                          ? playing
                            ? "예시 재생 중"
                            : "예시 재생 일시정지"
                          : run.outcome === "question"
                            ? "추가 조건 확인"
                            : run.status === "failed"
                              ? "조회 실패"
                              : run.status === "partial"
                                ? "확인 필요"
                                : "예시 검증 완료"}
                      </Status>
                    </div>
                    <Activity
                      compact
                      key={run.run_id}
                      run={run}
                      count={count}
                      playing={playing && tab === "explore"}
                    />
                    <div className="nv-actions playback">
                      {!ended && (
                        <>
                          <Button onClick={() => setPlaying(!playing)}>
                            {playing ? "예시 재생 일시정지" : "예시 재생 계속"}
                          </Button>
                          <Button
                            onClick={() => {
                              setCount(run.events.length);
                              setPlaying(false);
                            }}
                          >
                            예시 끝까지 보기
                          </Button>
                        </>
                      )}
                      {ended && run.outcome !== "question" && (
                        <Button primary onClick={() => setScreen("results")}>
                          결과 확인
                        </Button>
                      )}
                    </div>
                  </section>
                </>
              )}
              {screen === "question" && run && (
                <section className="nv-card question">
                  <h1 tabIndex={-1}>자녀가 어느 학년에 해당하나요?</h1>
                  <p className="nv-description">
                    후보마다 참여 대상이 달라요. 여러 자녀가 함께하면 해당
                    학년을 모두 선택해 주세요.
                  </p>
                  <div className="nv-card-content">
                    <GradeChoices value={answer} onChange={setAnswer} />
                  </div>
                  <div className="nv-actions nv-card-actions">
                    <Button
                      primary
                      disabled={!answer.length}
                      onClick={() =>
                        start({ ...run.conditions, grades: answer }, true)
                      }
                    >
                      이 조건으로 확인
                    </Button>
                    <Button onClick={() => start(run.conditions, true)}>
                      미정으로 계속 탐색
                    </Button>
                  </div>
                </section>
              )}
              {screen === "results" && run && (
                <>
                  <div className="page-heading">
                    <p className="eyebrow">YOUR FAMILY, YOUR EXPERIENCE</p>
                    <h1 tabIndex={-1}>{resultTitle}</h1>
                    <p>{run.next_action}</p>
                  </div>
                  <div className="results-toolbar">
                    <div className="condition-strip">
                      {summary.map((s, i) => (
                        <span key={i}>{s}</span>
                      ))}
                    </div>
                    <Button onClick={edit}>조건 수정</Button>
                  </div>
                  <div className="section-heading result-count">
                    <h2>
                      {run.candidates.length
                        ? `비교할 예시 후보 ${run.candidates.length}개`
                        : "확인 결과"}
                    </h2>
                    <Status state={state}>
                      {run.status === "failed"
                        ? "조회 미완료"
                        : run.status === "partial"
                          ? "확인 필요"
                          : "확인 완료"}
                    </Status>
                  </div>
                  {!run.candidates.length && (
                    <section className="nv-card empty-state">
                      <span className="empty-symbol" aria-hidden="true">
                        {run.outcome === "failed" ? "×" : "○"}
                      </span>
                      <h2>
                        {run.outcome === "failed"
                          ? "조회 실패와 후보 없음은 달라요"
                          : "조건을 조금 바꿔서 살펴볼까요?"}
                      </h2>
                      <p>{run.next_action}</p>
                      <div className="nv-actions">
                        <Button primary onClick={edit}>
                          조건 수정하기
                        </Button>
                        {run.outcome === "failed" && scenario !== "policy" && (
                          <Button onClick={() => start(run.conditions, true)}>
                            예시 다시 실행
                          </Button>
                        )}
                      </div>
                    </section>
                  )}
                  {mapPreview && run.candidates.length > 0 ? (
                    <MapResults key={run.run_id} candidates={run.candidates} />
                  ) : <div className="nv-card-grid results-grid">
                    {run.candidates.map((candidate) => (
                      <article className="nv-card candidate" key={candidate.id}>
                        <div
                          className={`candidate-art art-${candidate.interest}`}
                          aria-hidden="true"
                        >
                          <span>{interestLabels[candidate.interest]}</span>
                          <b>
                            {candidate.interest === "history"
                              ? "古"
                              : candidate.interest === "craft"
                                ? "結"
                                : "律"}
                          </b>
                          <small>ILLUSTRATIVE EXPERIENCE</small>
                        </div>
                        <div className="candidate-body">
                          <div className="section-heading">
                            <span className="eyebrow">
                              {candidate.district === "jongno"
                                ? "종로구"
                                : "중구"}{" "}
                              · 합성 예시
                            </span>
                            <Status
                              state={
                                candidate.verdict === "pass"
                                  ? "completed"
                                  : "hold"
                              }
                            >
                              {candidate.verdict === "pass"
                                ? "조건 확인"
                                : "확인 필요"}
                            </Status>
                          </div>
                          <h2>{candidate.title}</h2>
                          <p className="nv-description">
                            {candidate.experience}
                          </p>
                          <p className="recommendation">{candidate.reason}</p>
                          <dl className="candidate-meta">
                            <div>
                              <dt>장소</dt>
                              <dd>{candidate.place}</dd>
                            </div>
                            <div>
                              <dt>운영</dt>
                              <dd>
                                {candidate.dates
                                  .map((x) => x.slice(5).replace("-", "/"))
                                  .join(" · ")}
                                <br />
                                {candidate.time}
                              </dd>
                            </div>
                            <div>
                              <dt>참여비</dt>
                              <dd>{candidate.cost}</dd>
                            </div>
                            <div>
                              <dt>준비</dt>
                              <dd>{candidate.preparation}</dd>
                            </div>
                          </dl>
                          <ul className="checks">
                            {candidate.checks.map((check) => (
                              <li key={check.label}>
                                <Status
                                  state={
                                    check.verdict === "pass"
                                      ? "completed"
                                      : "hold"
                                  }
                                >
                                  {check.label}
                                </Status>
                                <span>{check.detail}</span>
                              </li>
                            ))}
                          </ul>
                          <details className="evidence">
                            <summary>판단 근거 확인</summary>
                            {candidate.evidence.map((e) => (
                              <div id={e.id} key={e.id}>
                                <strong>{e.title}</strong>
                                <blockquote>{e.quote}</blockquote>
                                <p className="nv-description">{e.source}</p>
                              </div>
                            ))}
                          </details>
                          <div className="candidate-actions">
                            <label className="compare-toggle">
                              <input
                                type="checkbox"
                                checked={compared.includes(candidate.id)}
                                onChange={() =>
                                  setCompared(toggle(compared, candidate.id))
                                }
                              />
                              비교에 담기
                            </label>
                            <button className="nv-button nv-secondary" disabled>
                              신청 링크 연결 전
                            </button>
                          </div>
                          <p className="small-note">
                            실제 기관·회차·잔여석을 확인한 결과가 아닙니다.
                          </p>
                        </div>
                      </article>
                    ))}
                  </div>}
                  {compared.length > 0 && (
                    <section className="comparison nv-card">
                      <div className="section-heading">
                        <h2>선택한 후보 비교 · {compared.length}개</h2>
                        <Button onClick={() => setCompared([])}>
                          비교 비우기
                        </Button>
                      </div>
                      {compared.length === 1 ? (
                        <p>
                          후보를 하나 더 담으면 조건을 나란히 비교할 수 있어요.
                        </p>
                      ) : (
                        <div className="nv-table-wrap">
                          <table className="nv-table">
                            <caption className="sr-only">
                              선택한 예시 체험 비교
                            </caption>
                            <thead>
                              <tr>
                                <th scope="col">비교 항목</th>
                                {run.candidates
                                  .filter((c) => compared.includes(c.id))
                                  .map((c) => (
                                    <th scope="col" key={c.id}>
                                      {c.title}
                                    </th>
                                  ))}
                              </tr>
                            </thead>
                            <tbody>
                              {[
                                "체험 내용",
                                "장소",
                                "운영 날짜",
                                "참여비",
                                "남은 확인",
                              ].map((label, index) => (
                                <tr key={label}>
                                  <th scope="row">{label}</th>
                                  {run.candidates
                                    .filter((c) => compared.includes(c.id))
                                    .map((c) => (
                                      <td key={c.id}>
                                        {
                                          [
                                            c.experience,
                                            c.place,
                                            c.dates.join(" · "),
                                            c.cost,
                                            c.checks
                                              .filter(
                                                (x) => x.verdict === "unknown",
                                              )
                                              .map((x) => x.detail)
                                              .join(" · ") ||
                                              "입력 조건 확인 · 실제 예약 가능 여부는 별도",
                                          ][index]
                                        }
                                      </td>
                                    ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </section>
                  )}
                  {run.excluded.length > 0 && (
                    <details className="execution-details">
                      <summary>
                        조건이 맞지 않아 제외한 예시 · {run.excluded.length}개
                      </summary>
                      {run.excluded.map((c) => (
                        <p key={c.id}>
                          <strong>{c.title}</strong> — {c.reason}
                        </p>
                      ))}
                    </details>
                  )}
                  <Security run={run} count={count} />
                </>
              )}
            </>
          )}
          {screen !== "analysis" && (
            <footer>
              <span>두루 · 함께하는 문화체험</span>
            </footer>
          )}
        </main>
      </div>
      <div className="sr-only" role="status" aria-live="polite">
        {tab === "explore" && screen === "analysis"
          ? !playing && !ended
            ? "예시 재생 일시정지"
            : run?.events[count - 1]?.label
          : screen === "results"
            ? resultTitle
            : ""}
      </div>
    </div>
  );
}
function Security({ run, count }: { run: Run; count: number }) {
  const denied =
    run.events
      .slice(0, count)
      .some((e) => e.kind === "tool" && e.status === "failed") &&
    run.scenario === "policy";
  return (
    <details className="security execution-details">
      <summary>
        실행·보안 기록 <span>MOCK · 실제 정책 검증 전</span>
      </summary>
      <p>
        이 화면은 도구 선택과 상태 표현을 확인하는 예시입니다. 실제 OpenShell
        허용·차단 결과는 아직 없습니다.
      </p>
      <dl>
        <div>
          <dt>실행 식별자</dt>
          <dd className="nv-technical">{run.run_id}</dd>
        </div>
        <div>
          <dt>외부 모델·자료 호출</dt>
          <dd>없음 · 브라우저의 합성 자료만 사용</dd>
        </div>
        <div>
          <dt>정책 집행</dt>
          <dd>
            {denied
              ? "미승인 목적지 차단을 가정한 예시 이벤트 수신"
              : "미검증 · 적용 정책 식별자 없음"}
          </dd>
        </div>
      </dl>
      <p className="nv-description">
        실제 연결 시 적용 정책·도구·허용 또는 거부 이유를 표시합니다. 공통 보안
        검사는 별도 CLI에서 수행합니다.
      </p>
    </details>
  );
}
