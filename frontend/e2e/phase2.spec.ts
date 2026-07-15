import { devices, expect, test } from "@playwright/test";

test("用户可注册并创建岗位订阅", async ({ page }) => {
  const email = `e2e-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`;

  await page.goto("/register");
  await page.getByLabel("姓名").fill("端到端测试用户");
  await page.getByLabel("邮箱").fill(email);
  await page.getByLabel("密码").fill("Playwright-2027!");
  await page.getByRole("button", { name: "注册并登录" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByRole("heading", { name: /继续向 Offer 出发/ })).toBeVisible();

  await page.goto("/alerts");
  await page.getByPlaceholder("订阅名称").fill("上海开发岗");
  await page.getByPlaceholder("岗位关键词").fill("开发");
  await page.getByPlaceholder("目标城市").fill("上海");
  await page.getByRole("button", { name: "创建", exact: true }).click();

  await expect(page.getByRole("heading", { name: "上海开发岗" })).toBeVisible();
  await expect(page.getByText("运行中", { exact: true })).toBeVisible();
});

test.describe("移动端", () => {
  const iphone = devices["iPhone 13"];
  test.use({
    deviceScaleFactor: iphone.deviceScaleFactor,
    hasTouch: iphone.hasTouch,
    isMobile: iphone.isMobile,
    userAgent: iphone.userAgent,
    viewport: iphone.viewport,
  });

  test("访客可以浏览 Demo 岗位并打开导航", async ({ page }) => {
    await page.goto("/jobs");
    await expect(page.getByRole("heading", { name: "岗位库" })).toBeVisible();
    await page.getByRole("button", { name: "打开主导航" }).click();
    await expect(page.getByRole("navigation")).toBeVisible();
    await expect(
      page.getByText("Demo", { exact: false }).first(),
    ).toBeVisible();
  });
});
