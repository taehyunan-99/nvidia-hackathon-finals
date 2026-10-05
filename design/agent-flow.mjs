import {renderFlow, renderResult, renderActivity} from '../.agents/skills/nvidia-ui/assets/agent-flow.mjs';
const $ = id => document.getElementById(id);
const liveSource = new URLSearchParams(location.search).get('source') === 'live';
const dataPath = liveSource ? '../runs/research-live.json' : '../docs/playbooks/examples/research/fixtures.json';
let fixtures, run, count = 0, selected = 0, timer = null;
function stop() { clearInterval(timer); timer = null; }
function totalSteps() { return run.events.length + ($('compare').checked ? fixtures.supplement.run.events.length : 0); }
function render() {
  const primaryCount = Math.min(count, run.events.length);
  const ended = count === totalSteps();
  $('mode').textContent = run.mode === 'live' ? `LIVE 모델 · 합성 도구 · HTTP ${run.http_requests}회` : 'MOCK · 합성 예시 · 외부 호출 0회';
  $('provenance').textContent = run.mode === 'live' ? '실제 모델이 선택한 합성 도구의 실행 기록입니다. 기록 재생이며 현재 API를 호출하지 않습니다.' : '규칙 기반 mock 판단과 로컬 합성 도구의 실행 기록입니다. 재생 속도는 실제 분석 시간이 아닙니다.';
  const view = renderFlow($('flow'), run, primaryCount, selected, seq => { selected = seq; render(); });
  renderResult($('result'), run, view);
  const candidates = $('compare').checked ? [{id: 'a', label: '후보 1 · 선택한 예시', run, count: primaryCount}, {id: 'b', label: '후보 2 · 추가 조사', run: fixtures.supplement.run, count: Math.max(0, Math.min(count - run.events.length, fixtures.supplement.run.events.length))}] : null;
  renderActivity($('activity'), run, primaryCount, {playing: timer !== null, candidates});
  $('step').disabled = ended || timer !== null;
  $('play').disabled = ended;
  $('play').textContent = timer === null ? '예시 재생' : '재생 일시정지';
  $('announcement').textContent = !count ? '입력 전 · 예시를 재생하세요.' : `표시 단계 ${count} · ${ended ? '예시 재생 종료' : timer !== null ? '재생 중' : '정지 화면'} · ${run.mode.toUpperCase()}`;
}
function advance() { count = Math.min(count + 1, totalSteps()); selected = run.events[Math.min(count, run.events.length) - 1]?.seq || 0; if (count === totalSteps()) stop(); render(); }
function reset() { stop(); run = fixtures[$('scenario').value].run; count = 0; selected = 0; render(); }
$('scenario').addEventListener('change', reset);
$('compare').addEventListener('change', reset);
$('reset').addEventListener('click', reset);
$('step').addEventListener('click', advance);
$('play').addEventListener('click', () => { if (timer !== null) stop(); else timer = setInterval(advance, 2800); render(); });
try {
  const response = await fetch(dataPath);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  fixtures = await response.json();
  for (const [key, value] of Object.entries(fixtures)) {
    const option = document.createElement('option'); option.value = key; option.textContent = value.label; $('scenario').append(option);
  }
  $('scenario').value = fixtures.supplement ? 'supplement' : Object.keys(fixtures)[0];
  $('data-link').href = dataPath;
  $('compare').disabled = liveSource;
  $('scenario').disabled = false; $('reset').disabled = false; reset();
} catch (error) {
  $('announcement').textContent = '예시를 불러오지 못했습니다.';
  $('load-error').hidden = false;
  $('load-error').textContent = `로컬 HTTP 서버로 열고 JSON 경로를 확인하세요. ${error.message}`;
}
