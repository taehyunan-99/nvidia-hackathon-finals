import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toRun } from '../src/live.ts';

test('live observations retain unknown and official sources without invented family ages', () => {
  const data = { request_id: 'test', conditions_revision: 1, question: null, action: 'finish_hold', reason: '조건 미확인', validator_connected: false,
    candidates: [{ id: 'S1', title: '실제 후보', place: '공식 장소', district: '중구', official_url: 'https://yeyak.seoul.go.kr/',
      operating_start: null, operating_end: null, cost: '무료', validation: { overall: 'unknown', checks: { age: { verdict: 'unknown', reason_code: 'missing_user_input', evidence_ids: [] } } },
      evidence: [{ id: 'e1', quote: '원문 근거', locator: 'API', source_id: 'api:S1' }] }],
    events: [{ kind: 'tool', name: 'get_experience_detail', status: 'ok' }, { kind: 'validation', status: 'unknown' }] };
  const run = toRun(data, { interests: ['craft'], grades: ['3'], guardians: '1', date: null, district: 'all' });
  assert.equal(run.mode, 'live'); assert.equal(run.status, 'partial'); assert.equal(run.candidates[0].verdict, 'unknown');
  assert.equal(run.candidates[0].evidence[0].source, 'https://yeyak.seoul.go.kr/');
  assert.deepEqual(run.candidates[0].grades, []); assert.deepEqual(run.candidates[0].dates, []);
  assert.equal(run.events[1].status, 'hold');
});


test('live progress stays running and preserves observed failures', () => {
  const run = toRun({ request_id: 'progress', conditions_revision: 2, question: null,
    action: 'running', reason: '', validator_connected: false, candidates: [],
    events: [{ kind: 'model', status: 'running' }, { kind: 'model', error_code: 'ValueError' }] },
    { interests: ['craft'], grades: [], guardians: 'unknown', date: null, district: 'all' });
  assert.equal(run.status, 'running');
  assert.equal(run.events[0].status, 'running');
  assert.equal(run.events[1].status, 'failed');
  assert.equal(run.conditionsRevision, 2);
  assert.deepEqual(run.candidates, []);
});
