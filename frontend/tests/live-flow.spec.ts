import { test, expect } from '@playwright/test';
test.skip(!process.env.AGENT_LIVE_BROWSER, 'Explicit live-mode browser adapter check');

test('live cards show observations and resume with owner and a new revision', async ({ page }) => {
  let revision = 1;
  let resumes = 0;
  const errors: string[] = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.route('**/api/runs**', async route => {
    const req = route.request();
    if (req.method() === 'POST' && req.url().endsWith('/resume')) {
      expect(req.headers()['x-run-owner']).toBe('owner-test');
      expect(req.postDataJSON().conditions_revision).toBe(1);
      expect(req.postDataJSON().selected_option_id).toBe('guardians-1');
      revision = 2; resumes++;
      await route.fulfill({ json: { run_id: 'test', conditions_revision: 2 } }); return;
    }
    if (req.method() === 'POST') { await route.fulfill({ status: 202, json: { run_id: 'test', owner_token: 'owner-test', conditions_revision: 1 } }); return; }
    if (req.method() === 'DELETE') throw new Error('Completed question must not be cancelled during resume');
    expect(req.headers()['x-run-owner']).toBe('owner-test');
    await route.fulfill({ json: { status: 'completed', result: {
      request_id: 'test', conditions_revision: revision, action: revision === 1 ? 'ask_user' : 'finish_hold', reason: '동반 조건 확인', validator_connected: true,
      conditions: { interests: ['craft'], district: 'all', children: null, guardians: revision === 1 ? null : { minimum: 1, maximum: 1 }, visit_date: null },
      question: revision === 1 ? { question_id: 'q1', field: 'guardians', member_id: null, options: [{ id: 'guardians-1', label: '보호자 1명' }, { id: 'guardians-2plus', label: '보호자 2명 이상' }] } : null,
      candidates: [{ id: 'S1', title: '공식 솟대 체험', place: '공식 문화기관', district: '중구', official_url: 'https://yeyak.seoul.go.kr/', cost: '무료', operating_start: null, operating_end: null,
        validation: { overall: 'unknown', checks: { age: { verdict: 'unknown', reason_code: 'missing_user_input', evidence_ids: [] } } }, evidence: [{ id: 'e1', quote: '공식 원문', source_id: 'api:S1', locator: 'API' }] }],
      events: [{ kind: 'tool', name: 'get_experience_detail', status: 'ok' }, { kind: 'validation', status: 'unknown' }] } } });
  });
  await page.goto('/');
  await page.getByRole('button', { name: /전통 공예 손으로/ }).click();
  await page.getByRole('button', { name: '다음', exact: true }).click();
  await page.getByRole('button', { name: '다음', exact: true }).click();
  await page.getByRole('button', { name: '체험 찾기', exact: true }).last().click();
  await expect(page.getByRole('heading', { name: '추가 조건을 확인해 주세요' })).toBeVisible();
  await expect(page.getByText('실제 탐색 · 공개 sample', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: '보호자 1명', exact: true }).click();
  await expect(page.getByRole('button', { name: '결과 확인', exact: true })).toBeVisible();
  await page.getByRole('button', { name: '결과 확인', exact: true }).click();
  await expect(page.getByRole('heading', { name: '공식 솟대 체험' })).toBeVisible();
  await expect(page.getByText('보호자 1명', { exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: '공식 신청 안내 확인' })).toHaveAttribute('href', 'https://yeyak.seoul.go.kr/');
  expect(resumes).toBe(1); expect(errors).toEqual([]);
});
