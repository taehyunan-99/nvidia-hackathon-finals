// Render only observable events. Domain payload stays in the service adapter.
const states = {empty: ['○', '입력 전'], running: ['…', '진행 중'], completed: ['✓', '완료'], hold: ['Ⅱ', '보류'], failed: ['×', '실패']};
const labels = {check_existing: '기존 근거 확인', collect_more: '추가 자료 조사'};
function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function badge(state, label) {
  const el = node('span', label ? `${states[state][0]} ${label}` : states[state].join(' '), 'nv-status');
  el.dataset.state = state;
  return el;
}
export function renderFlow(root, run, count, selected, onSelect) {
  const visible = run.events.slice(0, count);
  const ended = run.status !== 'running' && count === run.events.length;
  const state = !count ? 'empty' : ended ? {completed: 'completed', partial: 'hold', failed: 'failed', cancelled: 'hold'}[run.status] : 'running';
  const oldFocus = document.activeElement?.dataset?.eventSeq;
  root.replaceChildren();
  const header = node('div', undefined, 'nv-flow-heading');
  header.append(node('h2', '도구 선택과 분석 흐름', 'nv-card-title'), badge(state, ended && run.status === 'cancelled' ? '취소됨' : undefined));
  root.append(header, node('p', '각 카드는 당시의 관측 기록입니다. 단계를 선택하면 이유와 근거를 볼 수 있습니다.', 'nv-description'));
  const list = node('ol', undefined, 'nv-flow-path');
  for (const event of visible) {
    const item = node('li');
    const button = node('button', undefined, 'nv-flow-node');
    button.type = 'button';
    button.dataset.state = event.status;
    button.dataset.eventSeq = event.seq;
    button.setAttribute('aria-pressed', String(event.seq === selected));
    button.append(node('span', `${String(event.seq).padStart(2, '0')} · ${event.kind === 'tool' ? '도구' : event.kind === 'decision' ? '판단' : event.kind === 'validation' ? '검증' : '결과'}`, 'nv-description'));
    button.append(node('strong', labels[event.label] || event.label), badge(event.status, event.kind === 'decision' ? '선택 기록' : event.kind === 'tool' && event.status === 'running' ? '호출 시작' : undefined));
    button.addEventListener('click', () => onSelect(event.seq));
    item.append(button); list.append(item);
  }
  if (!count) list.append(node('li', '예시를 선택하고 재생하면 판단과 도구 호출이 여기에 나타납니다.', 'nv-description'));
  root.append(list);
  const detail = node('div', undefined, 'nv-flow-detail');
  const event = visible.find(e => e.seq === selected) || visible.at(-1);
  detail.append(node('h3', '선택 이유와 관측', 'nv-card-title'));
  detail.append(node('p', event?.reason || '아직 실행된 단계가 없습니다.', 'nv-description'));
  if (event?.tool) detail.append(node('p', `선택 도구: ${labels[event.tool]}${event.attempt ? ` · 시도 ${event.attempt}` : ''}`, 'nv-description'));
  if (event?.error_code) detail.append(node('p', `오류: ${event.error_code}`, 'nv-technical'));
  if (event?.evidence_ids.length) detail.append(node('p', `연결 근거: ${event.evidence_ids.join(', ')}`, 'nv-technical'));
  root.append(detail);
  if (oldFocus) root.querySelector(`[data-event-seq="${Number(oldFocus)}"]`)?.focus();
  return {visible, ended, state};
}
export function renderResult(root, run, view) {
  root.replaceChildren();
  root.append(node('h2', '결과와 근거', 'nv-card-title'));
  const shownIds = new Set(view.visible.flatMap(e => e.evidence_ids));
  const evidence = run.evidence.filter(e => shownIds.has(e.id));
  root.append(node('p', view.ended && run.artifact ? run.artifact.summary : view.ended ? '확정 결론 없음' : '검증된 결론을 기다리고 있습니다.', 'nv-description'));
  for (const row of evidence) {
    const card = node('div', undefined, 'nv-flow-evidence');
    card.id = row.id;
    card.append(node('strong', row.id), node('p', row.quote, 'nv-description'), node('p', row.source, 'nv-technical'));
    root.append(card);
  }
  if (!evidence.length) root.append(node('p', '표시할 근거가 아직 없습니다.', 'nv-description'));
  if (view.ended) {
    root.append(node('h3', '다음 행동', 'nv-card-title'), node('p', run.next_action, 'nv-description'));
  }
  root.append(node('p', run.limitations.join(' '), 'nv-flow-limit nv-description'));
}
