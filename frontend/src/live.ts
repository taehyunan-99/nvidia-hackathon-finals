import type { Conditions, Run, AssessedCandidate, Observation } from './contract';

interface Result {
  request_id: string; conditions_revision: number; question: Run["questionCard"]; action: string; reason: string; validator_connected: boolean;
  conditions?: { interests: Conditions['interests']; district: Conditions['district'];
    children: Conditions['children']; composition_complete: boolean; delivery_mode: Conditions['delivery_mode'];
    guardians: { minimum: number; maximum: number | null } | null; visit_date: string | null };
  candidates: { id: string; title: string; place: string; district: string; official_url: string;
    coordinates?: { latitude: number; longitude: number } | null; operating_start: string | null; operating_end: string | null; cost: string;
    validation: { overall: string; checks: Record<string, { verdict: string; reason_code: string; evidence_ids: string[] }> };
    evidence: { id: string; quote: string; locator: string; source_id: string }[] }[];
  events: { kind: string; name?: string; status?: string; reason?: string; candidate_id?: string; error_code?: string }[];
}
const owners = new Map<string, string>();
const labels: Record<string, string> = { age: '연령', grade: '학년', companions: '동반 조건', visit_date: '방문일', booking: '접수 상태', delivery: '운영 형태', interest: '관심 분야' };

export function toRun(data: Result, conditions: Conditions): Run {
  if (data.conditions) {
    const c = data.conditions;
    conditions = { ...conditions, children: c.children, composition_complete: c.composition_complete, delivery_mode: c.delivery_mode, interests: c.interests, district: c.district, date: c.visit_date,
      grades: c.children?.flatMap(child => child.grade ? [child.grade] : []) || [],
      guardians: c.guardians?.minimum === 2 && c.guardians.maximum === null ? '2+' :
        c.guardians && c.guardians.minimum === c.guardians.maximum && [0, 1, 2].includes(c.guardians.minimum) ?
          String(c.guardians.minimum) as '0' | '1' | '2' : 'unknown' };
  }
  const candidates: AssessedCandidate[] = data.candidates.filter(c => c.validation.overall !== 'unsuitable').map(c => ({
    id: c.id, title: c.title, testCoordinates: c.coordinates || undefined, interest: conditions.interests[0], district: conditions.district,
    districtLabel: c.district || '지역 미확인', officialUrl: c.official_url,
    experience: '공식 자료를 조회한 탐색 후보입니다. 참여 조건과 미확인 사항을 확인해 주세요.',
    place: c.place || '장소 미확인', dates: [], time: `운영기간 ${c.operating_start?.slice(0, 10) || '미확인'} ~ ${c.operating_end?.slice(0, 10) || '미확인'} · 회차는 근거 확인`,
    grades: [], guardianRequired: false, cost: c.cost, preparation: '공식 신청 페이지 확인',
    evidence: c.evidence.map(e => ({ id: e.id, title: e.locator, quote: e.quote, source: c.official_url })),
    checks: Object.entries(c.validation.checks).map(([field, check]) => ({ label: labels[field] || field,
      verdict: check.verdict === 'suitable' ? 'pass' : 'unknown',
      detail: check.verdict === 'suitable' ? '근거와 조건 일치' : check.reason_code === 'missing_user_input' ? '가족 조건 입력 필요' : check.reason_code.includes('conflict') ? '공식 자료의 차이 확인 필요' : '공식 근거 확인 필요', evidenceId: check.evidence_ids[0] || '' })),
    verdict: c.validation.overall === 'suitable' ? 'pass' : 'unknown', reason: data.validator_connected ? data.reason : '조건 검증기 연결 전입니다. 참여 적합성은 미확인입니다.',
  }));
  const reason = data.reason.startsWith('execution_failed:') ? '탐색이 중간에 종료되었습니다. 확인한 자료만 표시하며 나머지는 미확인입니다.' : data.reason.startsWith('execution_limit:') ? '실행 한도에 도달했습니다. 확인한 자료만 표시합니다.' : data.action === 'finish_results' ? '공식 조건과 일치한 후보입니다. 실제 회차와 잔여석은 신청 안내에서 확인해 주세요.' : '공식 자료에서 확인한 후보입니다. 확인 필요 항목을 살펴보고 날짜와 가족 조건을 보완해 주세요.';
  const failed = data.action === 'finish_failed';
  const names: Record<string, string> = { search_experiences: '후보 조회', get_experience_detail: '상세 근거 확인', read_official_source: '공식 보충 자료 확인' };
  const events: Observation[] = data.events.map((event, i) => ({ seq: i + 1,
    kind: event.kind === 'tool' || event.kind === 'model' ? 'tool' : event.kind === 'validation' ? 'validation' : event.kind === 'result' ? 'result' : 'decision',
    label: event.kind === 'model' ? event.status === 'running' ? '모델 판단 준비' : '모델 판단 응답' : (event.name && names[event.name]) || (event.kind === 'validation' ? '조건 검증' : '실행 결과'),
    reason: event.reason || event.candidate_id || '실제 실행에서 관측한 이벤트',
    status: event.status === 'running' ? 'running' : event.error_code || event.status === 'error' || event.status === 'policy_denied' ? 'failed' : event.kind === 'validation' && event.status !== 'suitable' ? 'hold' : 'completed',
    evidence_ids: [], tool: event.kind === 'model' ? 'model' : event.kind === 'validation' ? 'validate' : event.name === 'search_experiences' ? 'search' : event.name === 'get_experience_detail' ? 'detail' : event.name === 'read_official_source' ? 'official' : undefined,
  }));
  return { run_id: data.request_id, mode: 'live', conditions, scenario: 'normal',
    status: data.action === 'running' ? 'running' : failed ? 'failed' : data.action === 'finish_results' ? 'completed' : 'partial',
    questionCard: data.question,
    conditionsRevision: data.conditions_revision,
    outcome: data.action === 'ask_user' ? 'question' : failed ? 'failed' : data.action === 'finish_limited' ? 'limited' : data.action === 'finish_no_candidates' ? 'empty' : 'results',
    question: null, events, candidates,
    excluded: data.candidates.filter(c => c.validation.overall === 'unsuitable').map(c => ({ id: c.id, title: c.title, reason: '공식 조건과 불일치' })),
    next_action: reason + ' · 서울 공개 sample 범위입니다. 전체 후보와 잔여석은 확인되지 않았습니다.',
  };
}

function pendingRun(conditions: Conditions): Run {
  return toRun({ request_id: 'pending', conditions_revision: 1, action: 'running',
    reason: '', question: null, validator_connected: false, candidates: [], events: [] }, conditions);
}

export async function liveRun(conditions: Conditions, signal: AbortSignal, onProgress?: (run: Run) => void): Promise<Run> {
  onProgress?.(pendingRun(conditions));
  const response = await fetch('/api/runs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(conditions) });
  if (!response.ok) throw new Error('탐색 요청을 접수하지 못했습니다.');
  const job = await response.json();
  owners.set(job.run_id, job.owner_token);
  if (signal.aborted) { cancelLive(job.run_id); throw new DOMException("Aborted", "AbortError"); }
  const cancel = () => cancelLive(job.run_id);
  signal.addEventListener("abort", cancel, { once: true });
  try { return await poll(job.run_id, conditions, signal, onProgress); }
  finally { signal.removeEventListener("abort", cancel); }
}

export function cancelLive(runId: string) {
  const owner = owners.get(runId);
  if (!owner) return;
  owners.delete(runId);
  void fetch(`/api/runs/${runId}`, { method: 'DELETE', headers: { 'X-Run-Owner': owner } }).catch(() => {});
}

export async function resumeLive(run: Run, option: string, signal: AbortSignal, onProgress?: (run: Run) => void): Promise<Run> {
  if (!run.questionCard) throw new Error('현재 질문이 없습니다.');
  onProgress?.(pendingRun(run.conditions));
  const cancel = () => cancelLive(run.run_id);
  signal.addEventListener('abort', cancel, { once: true });
  try {
  const response = await fetch(`/api/runs/${run.run_id}/resume`, { method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Run-Owner': owners.get(run.run_id) || '' },
    body: JSON.stringify({ question_id: run.questionCard.question_id, request_id: run.run_id,
      conditions_revision: run.conditionsRevision, selected_option_id: option }), signal });
  if (!response.ok) throw new Error('질문 응답을 반영하지 못했습니다. 조건을 수정해 주세요.');
  return await poll(run.run_id, run.conditions, signal, onProgress);
  } finally { signal.removeEventListener('abort', cancel); }
}

async function poll(runId: string, conditions: Conditions, signal: AbortSignal, onProgress?: (run: Run) => void): Promise<Run> {
  for (let i = 0; i < 500; i++) {
    if (signal.aborted) throw new DOMException('Aborted', 'AbortError');
    const state = await fetch(`/api/runs/${runId}`, { headers: { 'X-Run-Owner': owners.get(runId) || '' }, signal });
    if (!state.ok) throw new Error('실행 상태를 확인하지 못했습니다.');
    const data = await state.json();
    if (data.status === 'cancelled') throw new Error('탐색이 취소되었습니다.');
    if (data.status === 'failed') throw new Error('탐색 실행에 실패했습니다. 조건을 확인하고 다시 시도해 주세요.');
    if (data.status === 'completed') return toRun(data.result, conditions);
    if (onProgress && Array.isArray(data.events)) onProgress(toRun({
      request_id: runId, conditions_revision: data.conditions_revision, action: 'running',
      reason: '', question: null, validator_connected: false, candidates: [], events: data.events,
    }, conditions));
    await new Promise<void>(resolve => setTimeout(resolve, 2000));
  }
  throw new Error('실행 상태 확인 시간이 끝났습니다.');
}
