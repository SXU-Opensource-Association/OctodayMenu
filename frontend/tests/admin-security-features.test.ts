import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const apiSource = readFileSync(new URL("../lib/api.ts", import.meta.url), "utf8");
const adminSource = readFileSync(new URL("../components/admin-dashboard.tsx", import.meta.url), "utf8");
const authSource = readFileSync(new URL("../components/auth-form.tsx", import.meta.url), "utf8");
const nextConfigSource = readFileSync(new URL("../next.config.mjs", import.meta.url), "utf8");

test("browser authentication uses cookie credentials without persisting access tokens", () => {
  assert.doesNotMatch(apiSource, /localStorage\.setItem/);
  assert.match(apiSource, /credentials: "same-origin"/);
  assert.match(apiSource, /\/auth\/logout/);
});

test("development and production builds use isolated Next.js chunk directories", () => {
  assert.match(nextConfigSource, /distDir: isProduction \? "\.next" : "\.next-dev"/);
});

test("admin login renders the email MFA challenge", () => {
  assert.match(authSource, /adminMfaRequired/);
  assert.match(authSource, /管理员验证码/);
  assert.match(authSource, /mfa_required/);
});

test("admin workspace exposes audit logs, transfer, CRUD and image replacement", () => {
  assert.match(adminSource, /项目日志/);
  assert.match(adminSource, /transferSuperAdmin/);
  assert.match(adminSource, /deleteFoodArea/);
  assert.match(adminSource, /deleteFoodSection/);
  assert.match(adminSource, /deleteVendor/);
  assert.match(adminSource, /deleteDish/);
  assert.match(adminSource, /deleteTag/);
  assert.match(adminSource, /uploadImage/);
  assert.match(adminSource, /山西大学西侧小吃街/);
  assert.match(adminSource, /blacklistUser/);
  assert.match(adminSource, /muteUser/);
  assert.match(adminSource, /发布公告/);
  assert.match(adminSource, /deleteAnnouncement/);
});
