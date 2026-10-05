// Render only observable events. Domain payload stays in the service adapter.
const states = {empty: ['○', '입력 전'], running: ['…', '진행 중'], completed: ['✓', '완료'], hold: ['!', '보류'], failed: ['×', '실패']};
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
  if (event?.tool) detail.append(node('p', `선택 도구: ${labels[event.tool] || event.tool}${event.attempt ? ` · 시도 ${event.attempt}` : ''}`, 'nv-description'));
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

// Keep graph nodes alive across events so visual transitions do not restart.
export const ACTIVITY_RULES = Object.freeze({
  version: 'activity-v1',
  maxCandidates: 4,
  coreRadius: 64,
  toolRadius: 34,
  candidateRingOffset: 8,
  candidateRingStep: 7,
  candidateColors: Object.freeze(['#426700', '#2879ce', '#9460cf', '#d17a20']),
});
const activityViews = new WeakMap();
export function renderActivity(root, run, count, {tools = labels, playing = false, candidates = null} = {}) {
  const visible = run.events.slice(0, count), latest = visible.at(-1);
  const ended = count === run.events.length && run.status !== 'running';
  const phase = !latest ? '입력 전' : ended ? (run.status === 'completed' ? '검증 후 완료' : run.status === 'failed' ? '실행 실패' : '보류·중단')
    : latest.kind === 'decision' ? (latest.tool ? '도구 선택 · 호출 전' : '실행 제어의 종료')
    : latest.kind === 'validation' ? '근거 검증' : latest.kind === 'tool' ? (latest.status === 'running' ? '호출 중' : latest.status === 'failed' ? '호출 실패' : '응답 수신') : latest.label;
  // Explicit candidate IDs own rings and routes; a plain run has no candidate rings.
  const tracks = candidates ? [...candidates].sort((a, b) => a.id.localeCompare(b.id)) : [{id: run.run_id, label: '현재 실행', run, count}];
  const colors = ACTIVITY_RULES.candidateColors;
  if (candidates && (!tracks.length || tracks.length > ACTIVITY_RULES.maxCandidates || new Set(tracks.map(c => c.id)).size !== tracks.length)) throw new Error('후보는 고유 ID를 가진 1~4개여야 합니다.');
  const key = JSON.stringify([run.run_id, tools, candidates && tracks.map(c => [c.id, c.label])]);
  let view = activityViews.get(root);
  if (!view || view.key !== key || !root.contains(view.svg)) {
    function svgNode(tag, attrs, text) {
      const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
      for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
      if (text !== undefined) el.textContent = text;
      return el;
    }
    const entries = Object.entries(tools);
    const svg = svgNode('svg', {viewBox: entries.length === 2 ? '0 85 920 315' : '0 0 920 500', class: 'nv-activity-map', role: 'img'});
    const status = node('p', '', 'nv-description');
    const reason = node('p', '', 'nv-activity-reason nv-description');
    view = {key, svg, status, reason, tools: [], rings: [], legend: node('div', '', 'nv-activity-legend')};
    tracks.forEach((track, index) => {
      const item = node('span', '', 'nv-activity-legend-item');
      item.style.setProperty('--track-color', colors[index % colors.length]);
      const dot = node('span', String(index + 1), 'nv-activity-track-dot');
      const text = node('span');
      if (candidates) item.append(dot);
      item.append(text); view.legend.append(item);
    });
    view.legendTexts = [...view.legend.querySelectorAll('.nv-activity-legend-item > span:last-child')];
    const icons = {
      check_existing: 'M7 7L17 17M10 -3A13 13 0 1 1 -16 -3A13 13 0 1 1 10 -3',
      collect_more: 'M-12 -15H5L12 -8V15H-12ZM5 -15V-8H12M-6 -1H6M-6 6H3',
    };
    entries.forEach(([id, label], index) => {
      const angle = entries.length === 2 ? Math.PI + index * Math.PI : -Math.PI / 2 + index * Math.PI * 2 / entries.length;
      const dx = Math.cos(angle) * 290, dy = Math.sin(angle) * 165, length = Math.hypot(dx, dy);
      const x = 460 + dx, y = 245 + dy;
      // Edge-to-edge paths avoid signals disappearing behind node bodies.
      const path = `M${460+dx/length*64} ${245+dy/length*64} Q${460+dx/2} ${245+dy/2-14} ${x-dx/length*34} ${y-dy/length*34}`;
      const group = svgNode('g', {transform: `translate(${x} ${y})`, 'data-state': 'empty'});
      group.append(svgNode('circle', {r: ACTIVITY_RULES.toolRadius, class: 'nv-activity-tool'}));
      group.append(svgNode('path', {d: icons[id] || 'M0 -15L14 -7V9L0 17L-14 9V-7ZM-14 -7L0 1L14 -7M0 1V17', class: 'nv-activity-icon'}));
      const caption = svgNode('text', {x: 0, y: 86 + (candidates ? tracks.length * 5 : 0), class: 'nv-activity-caption'});
      group.append(svgNode('text', {x: 0, y: 66 + (candidates ? tracks.length * 5 : 0), class: 'nv-activity-label'}, label), caption);
      const route = svgNode('path', {d: path, class: 'nv-activity-route'});
      const signal = svgNode('path', {d: path, pathLength: 100, class: 'nv-activity-signal', 'aria-hidden': true});
      const rings = [];
      if (candidates) tracks.forEach((track, trackIndex) => {
        const ring = svgNode('circle', {r: ACTIVITY_RULES.toolRadius + ACTIVITY_RULES.candidateRingOffset + trackIndex * ACTIVITY_RULES.candidateRingStep, class: 'nv-activity-candidate-ring', 'data-candidate-id': track.id});
        ring.style.setProperty('--track-color', colors[trackIndex]);
        group.append(ring); rings.push(ring);
      });
      svg.append(route, signal);
      view.tools.push({id, route, signal, group, caption, rings});
      svg.append(group);
    });
    const core = svgNode('g', {transform: 'translate(460 245)'});
    core.append(svgNode('circle', {r: ACTIVITY_RULES.coreRadius, class: 'nv-activity-core'}));
    if (candidates) tracks.forEach((track, index) => {
      const ring = svgNode('circle', {r: ACTIVITY_RULES.coreRadius + ACTIVITY_RULES.candidateRingOffset + index * ACTIVITY_RULES.candidateRingStep, class: 'nv-activity-candidate-ring', 'data-candidate-id': track.id});
      ring.style.setProperty('--track-color', colors[index % colors.length]);
      core.append(ring); view.rings.push(ring);
    });
    core.append(svgNode('path', {d: 'M-24 -17L0 -33L24 -17L0 -1ZM-24 -17H24M0 -33V-1', class: 'nv-activity-neural'}));
    for (const [cx,cy] of [[-24,-17],[0,-33],[24,-17],[0,-1],[0,-17]]) core.append(svgNode('circle', {cx,cy,r:2.5,class:'nv-activity-neural-dot'}));
    view.coreCaption = svgNode('text', {x: 0, y: 40, class: 'nv-activity-caption'});
    core.append(svgNode('text', {x: 0, y: 20, class: 'nv-activity-core-title'}, 'AGENT'), view.coreCaption);
    svg.append(core);
    root.replaceChildren(node('h2', '에이전트와 도구', 'nv-card-title'), status, view.legend, svg, reason);
    activityViews.set(root, view);
  }
  const observations = tracks.map(track => {
    const events = track.run.events.slice(0, track.count);
    const event = events.at(-1);
    const terminal = track.count === track.run.events.length && track.run.status !== 'running';
    return {events, event, terminal, active: !terminal && ['decision', 'tool'].includes(event?.kind) ? event.tool : null};
  });
  view.svg.setAttribute('aria-label', `도구 선택 지도: ${candidates ? `${tracks.length}개 후보 비교` : phase}`);
  view.status.textContent = candidates ? '후보 순차 처리 · 합성 기록 재생' : `${phase} · ${playing ? '기록 재생 중' : '정지 화면'}`;
  view.reason.textContent = candidates ? '같은 번호·색상은 같은 후보입니다. 링은 안쪽부터 범례 순서이며, 이동 신호는 호출 중인 후보에만 표시합니다. 아래 상세 기록과 결과는 후보 1 기준입니다.' : latest?.reason || '실행 전에는 모든 도구가 미선택입니다.';
  view.coreCaption.textContent = candidates ? `${tracks.length}개 후보` : latest?.kind === 'decision' && latest.tool ? '도구 선택' : latest?.kind === 'validation' ? '근거 검증' : ended ? '실행 종료' : '실행 제어';
  observations.forEach((observation, index) => {
    const {event, terminal} = observation;
    view.legendTexts[index].textContent = candidates ? `${tracks[index].label} · ${terminal ? states[{completed:'completed',partial:'hold',failed:'failed',cancelled:'hold'}[tracks[index].run.status]][1] : event ? `${tools[event.tool] || event.label} · ${event.kind === 'decision' ? '선택' : states[event.status][1]}` : '입력 전'}` : '노드 테두리 = 에이전트·도구 · 선 = 연결 · 이동 신호 = 호출 중';
    if (view.rings[index]) {
      view.rings[index].dataset.visited = Boolean(event);
      view.rings[index].dataset.state = terminal ? {completed:'completed',partial:'hold',failed:'failed',cancelled:'hold'}[tracks[index].run.status] : event?.status || 'empty';
    }
  });
  const activeIndices = observations.flatMap((o, i) => o.active ? [i] : []);
  const current = activeIndices.length === 1 ? activeIndices[0] : -1;
  if (activeIndices.length > 1) view.status.textContent = '순차 실행 계약 확인 필요 · 동시에 활성인 후보 기록';
  for (const item of view.tools) {
    observations.forEach((observation, index) => {
      const last = observation.events.findLast(e => e.tool === item.id);
      const ring = item.rings[index];
      if (ring) {
        ring.dataset.state = !last ? 'empty' : last.kind === 'decision' ? 'running' : last.status;
        ring.dataset.visited = Boolean(last);
        ring.dataset.active = observation.active === item.id;
      }
    });
    const observation = observations[current] || observations.at(-1);
    const active = current >= 0 && observation.active === item.id;
    const last = observation.events.findLast(e => e.tool === item.id);
    const state = !last ? 'empty' : last.kind === 'decision' ? 'running' : last.status;
    for (const el of [item.route, item.group]) {
      el.dataset.state = candidates ? 'empty' : state;
      el.dataset.active = active;
      el.dataset.visited = observations.some(o => o.events.some(e => e.tool === item.id));
    }
    for (const el of [item.route, item.signal]) el.style.setProperty('--track-color', candidates && active ? colors[current] : 'var(--state-ink,var(--accent-ink))');
    item.signal.classList.toggle('is-running', playing && active && observation.event?.kind === 'tool' && observation.event.status === 'running');
    const status = !last ? '미선택' : last.kind === 'decision' ? '선택 · 호출 전' : last.status === 'running' ? '호출 중' : last.status === 'failed' ? '× 호출 실패' : '✓ 응답 수신';
    item.caption.textContent = candidates ? active ? `후보 ${current+1} · ${status}` : '현재 호출 없음' : status + (last?.attempt ? ` · 시도 ${last.attempt}` : '');
  }
}
