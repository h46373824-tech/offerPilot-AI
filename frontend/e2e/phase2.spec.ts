import { devices, expect, test } from "@playwright/test";

test("用户可注册并创建岗位订阅", async ({ page }) => {
  const email = `e2e-${Date.now()}-${Math.random().toString(16).slice(2)}@example.com`;

  await page.goto("/register");
  await page.getByLabel("姓名").fill("端到端测试用户");
  await page.getByLabel("邮箱").fill(email);
  await page.getByLabel("密码").fill("Playwright-2027!");
  await page.getByRole("button", { name: "注册并登录" }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(
    page.getByRole("heading", { name: /继续向 Offer 出发/ }),
  ).toBeVisible();

  await page.goto("/alerts");
  await page.getByPlaceholder("订阅名称").fill("上海开发岗");
  await page.getByPlaceholder("岗位关键词").fill("开发");
  await page.getByPlaceholder("目标城市").fill("上海");
  await page.getByRole("button", { name: "创建", exact: true }).click();

  await expect(page.getByRole("heading", { name: "上海开发岗" })).toBeVisible();
  await expect(page.getByText("运行中", { exact: true })).toBeVisible();
});

test("本地管理员可以登记授权数据源", async ({ page }) => {
  const credentials = {
    email: "admin@offerpilot.example.com",
    password: "Local-Admin-2027!",
  };
  const apiUrl = process.env.E2E_API_URL ?? "http://localhost:8000/api/v1";
  const registered = await page.request.post(`${apiUrl}/auth/register`, {
    data: { ...credentials, full_name: "本地管理员" },
  });
  const authResponse = registered.ok()
    ? registered
    : await page.request.post(`${apiUrl}/auth/login`, { data: credentials });
  expect(authResponse.ok()).toBeTruthy();
  const { access_token: token } = (await authResponse.json()) as {
    access_token: string;
  };
  await page.goto("/");
  await page.evaluate(
    (accessToken) => localStorage.setItem("access_token", accessToken),
    token,
  );

  await page.goto("/admin");
  await expect(
    page.getByRole("heading", { name: "本地数据治理" }),
  ).toBeVisible();
  const sourceName = `端到端授权源-${Date.now()}`;
  await page.getByPlaceholder("数据源名称").fill(sourceName);
  await page
    .getByPlaceholder("授权范围、用途与有效期")
    .fill("仅限本机端到端测试使用");
  await page.getByRole("button", { name: "登记数据源" }).click();
  await expect(
    page.getByText(`${sourceName} · 启用`, { exact: true }),
  ).toBeVisible();
});

test("岗位库可以跳转到官方投递链接", async ({ page }) => {
  const credentials = {
    email: "admin@offerpilot.example.com",
    password: "Local-Admin-2027!",
  };
  const apiUrl = process.env.E2E_API_URL ?? "http://localhost:8000/api/v1";
  const registered = await page.request.post(`${apiUrl}/auth/register`, {
    data: { ...credentials, full_name: "投递链接测试管理员" },
  });
  const authResponse = registered.ok()
    ? registered
    : await page.request.post(`${apiUrl}/auth/login`, { data: credentials });
  expect(authResponse.ok()).toBeTruthy();
  const { access_token: token } = (await authResponse.json()) as {
    access_token: string;
  };
  const headers = { Authorization: `Bearer ${token}` };
  const suffix = Date.now();
  const company = await page.request.post(`${apiUrl}/companies`, {
    data: {
      name: `投递链接测试企业-${suffix}`,
      industry: "人工智能",
      company_type: "测试",
      education_requirement: "待核验",
      work_cities: "待核验",
    },
    headers,
  });
  expect(company.ok()).toBeTruthy();
  const companyId = (await company.json()).id as number;
  const title = `官方投递测试岗位-${suffix}`;
  const applicationUrl = `https://careers.example.com/apply/${suffix}`;
  const job = await page.request.post(`${apiUrl}/jobs`, {
    data: {
      title,
      company_id: companyId,
      category: "测试",
      work_cities: "待核验",
      education_requirement: "待核验",
      description: "端到端测试",
      requirements: "待核验",
      application_url: applicationUrl,
      recruitment_status: "unverified",
    },
    headers,
  });
  expect(job.ok()).toBeTruthy();

  await page.goto("/");
  await page.evaluate(
    (accessToken) => localStorage.setItem("access_token", accessToken),
    token,
  );
  await page.goto("/jobs");
  await page.getByPlaceholder("输入关键词搜索").fill(title);
  const link = page.getByRole("link", { name: "前往官方投递" });
  await expect(link).toHaveAttribute("href", applicationUrl);
  await expect(link).toHaveAttribute("target", "_blank");

  await page.request.delete(`${apiUrl}/companies/${companyId}`, { headers });
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
