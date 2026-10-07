import { test, expect, type Page } from "@playwright/test";
async function input(page: Page, scenario?: string) {
  await page.goto(scenario ? "/?demo=1" : "/");
  await expect(
    page.getByRole("button", { name: "다음", exact: true }),
  ).toBeDisabled();
  await page.getByRole("button", { name: /역사 탐방 옛 이야기/ }).click();
  await page.getByRole("button", { name: /전통 공예 손으로/ }).click();
  if (scenario) {
    await page.getByText("화면 검증용 예시 설정", { exact: true }).click();
    await page.getByRole("button", { name: scenario, exact: true }).click();
  }
  await page.getByRole("button", { name: "다음", exact: true }).click();
}
async function finish(page: Page) {
  await page
    .getByRole("button", { name: "예시 끝까지 보기", exact: true })
    .click();
  await page.getByRole("button", { name: "결과 확인", exact: true }).click();
}
test("input, observation, evidence, comparison and team round trip", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await input(page);
  await page.getByRole("button", { name: "초등 2학년", exact: false }).click();
  await page.getByRole("button", { name: "1명", exact: false }).click();
  await page.getByRole("button", { name: "다음", exact: true }).click();
  await page.getByRole("button", { name: /10월 10일/ }).click();
  await page
    .getByRole("button", { name: "예시 체험 찾기", exact: true })
    .click();
  await expect(page.getByText("에이전트 분석", { exact: true })).toBeVisible();
  await page
    .getByRole("button", { name: "예시 재생 일시정지", exact: true })
    .click();
  await page.getByRole("button", { name: "팀원 소개", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "안태현", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "조수빈", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "체험 찾기", exact: true }).click();
  await page
    .getByRole("button", { name: "이전 분석 보기", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "예시 재생 계속", exact: true }),
  ).toBeVisible();
  await finish(page);
  await expect(
    page.getByText("비교할 예시 후보 2개", { exact: true }),
  ).toBeVisible();
  const checks = page.getByRole("checkbox", { name: "비교에 담기" });
  await checks.nth(0).check();
  await checks.nth(1).check();
  await expect(page.getByRole("table")).toBeVisible();
  await page.getByText("판단 근거 확인", { exact: true }).first().click();
  await expect(
    page.getByText("참여조건 안내 · 합성 자료", { exact: true }).first(),
  ).toBeVisible();
  expect(errors).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
test("unknown conditions ask a card question and stay unconfirmed after skip", async ({
  page,
}) => {
  await input(page);
  await page.getByRole("button", { name: "다음", exact: true }).click();
  await page
    .getByRole("button", { name: "예시 체험 찾기", exact: true })
    .click();
  await page
    .getByRole("button", { name: "예시 끝까지 보기", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "자녀가 어느 학년에 해당하나요?" }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "미정으로 계속 탐색", exact: true })
    .click();
  await finish(page);
  await expect(
    page.getByRole("heading", { name: "이런 체험은 어떠세요?" }),
  ).toBeVisible();
  await expect(
    page.getByText("자녀 학년 미입력", { exact: true }).first(),
  ).toBeVisible();
  await page.getByRole("button", { name: "조건 수정", exact: true }).click();
  await expect(
    page.getByRole("heading", {
      name: "우리 가족의 다음 문화체험",
    }),
  ).toBeVisible();
  await expect(page.getByRole("checkbox", { name: "비교에 담기" })).toHaveCount(
    0,
  );
});
for (const [scenario, heading] of [
  ["후보 없음", "조건에 맞는 후보가 없어요"],
  ["조회 실패", "자료를 확인하지 못했어요"],
  ["정책 거부", "자료를 확인하지 못했어요"],
  ["자료 충돌", "이런 체험은 어떠세요?"],
  ["실행 한도 종료", "확인한 후보부터 살펴보세요"],
]) {
  test(`${scenario} is distinct and preserves honest security labels`, async ({
    page,
  }) => {
    await input(page, scenario);
    await page
      .getByRole("button", { name: "초등 2학년", exact: false })
      .click();
    await page.getByRole("button", { name: "1명", exact: false }).click();
    await page.getByRole("button", { name: "다음", exact: true }).click();
    await page.getByRole("button", { name: /10월 10일/ }).click();
    await page
      .getByRole("button", { name: "예시 체험 찾기", exact: true })
      .click();
    await finish(page);
    await expect(
      page.getByRole("heading", { name: heading, exact: true }),
    ).toBeVisible();
    await page.getByText("실행·보안 기록", { exact: false }).click();
    await expect(
      page.getByText("MOCK · 실제 정책 검증 전", { exact: true }),
    ).toBeVisible();
  });
}
test("keyboard and reduced motion at compact desktop width", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1024, height: 900 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const choice = page.getByRole("button", { name: /역사 탐방 옛 이야기/ });
  await choice.focus();
  await page.keyboard.press("Enter");
  await expect(choice).toHaveAttribute("aria-pressed", "true");
  await expect(
    page.getByRole("button", { name: "다음", exact: true }),
  ).toBeEnabled();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("additional answer resumes with new conditions; failed avatars retain names", async ({
  page,
}) => {
  await page.route("https://avatars.githubusercontent.com/**", (route) =>
    route.abort(),
  );
  await input(page);
  await page.getByRole("button", { name: "다음", exact: true }).click();
  await page
    .getByRole("button", { name: "예시 체험 찾기", exact: true })
    .click();
  await page
    .getByRole("button", { name: "예시 끝까지 보기", exact: true })
    .click();
  await page.getByRole("button", { name: "초등 3학년", exact: false }).click();
  await page
    .getByRole("button", { name: "이 조건으로 확인", exact: true })
    .click();
  await finish(page);
  await expect(page.getByText("초등 3학년", { exact: true })).toBeVisible();
  await expect(page.getByText("자녀 학년 미입력", { exact: true })).toHaveCount(
    0,
  );
  await page.getByRole("button", { name: "팀원 소개", exact: true }).click();
  await expect(page.locator(".avatar").first()).toHaveText("안");
  await expect(page.locator(".avatar").last()).toHaveText("조");
});

test("tool labels and response captions stay clear of routes and inside the map", async ({
  page,
}) => {
  await input(page);
  await page.getByRole("button", { name: "다음", exact: true }).click();
  await page
    .getByRole("button", { name: "예시 체험 찾기", exact: true })
    .click();
  await expect(
    page
      .locator(".nv-activity-caption")
      .filter({ hasText: "응답 수신" })
      .first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "예시 재생 일시정지", exact: true })
    .click();
  for (const width of [1024, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    const issues = await page.locator(".nv-activity-map").evaluate((svg) => {
      const errors: string[] = [];
      const frame = svg.getBoundingClientRect();
      const labels = [
        ...svg.querySelectorAll(".nv-activity-label, .nv-activity-caption"),
      ];
      for (const label of labels) {
        const box = label.getBoundingClientRect();
        if (!box.width) continue;
        if (
          box.left < frame.left ||
          box.right > frame.right ||
          box.top < frame.top ||
          box.bottom > frame.bottom
        )
          errors.push(`clipped: ${label.textContent}`);
        for (const route of svg.querySelectorAll<SVGPathElement>(
          ".nv-activity-route",
        )) {
          const length = route.getTotalLength();
          for (let i = 0; i <= 100; i++) {
            const local = route.getPointAtLength((length * i) / 100);
            const point = new DOMPoint(local.x, local.y).matrixTransform(
              route.getScreenCTM()!,
            );
            if (
              point.x > box.left - 3 &&
              point.x < box.right + 3 &&
              point.y > box.top - 3 &&
              point.y < box.bottom + 3
            ) {
              errors.push(`route overlaps: ${label.textContent}`);
              break;
            }
          }
        }
      }
      return errors;
    });
    expect(issues).toEqual([]);
  }
});

test("brand and explore always return home while inputs survive reload within the tab", async ({
  page,
  context,
}) => {
  await input(page);
  await page.getByRole("button", { name: "초등 2학년", exact: false }).click();
  await page.getByRole("button", { name: "두루 홈", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "우리 가족의 다음 문화체험" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /역사 탐방 옛 이야기/ }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.reload();
  await expect(
    page.getByRole("button", { name: /역사 탐방 옛 이야기/ }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "다음", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "초등 2학년", exact: false }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "체험 찾기", exact: true }).click();
  await expect(
    page.getByRole("button", { name: /역사 탐방 옛 이야기/ }),
  ).toBeVisible();
  const fresh = await context.newPage();
  await fresh.goto("/");
  await expect(
    fresh.getByRole("button", { name: /역사 탐방 옛 이야기/ }),
  ).toHaveAttribute("aria-pressed", "false");
  await fresh.close();
});
