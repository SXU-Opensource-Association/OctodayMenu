import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const authFormSource = readFileSync(new URL("../components/auth-form.tsx", import.meta.url), "utf8");

test("login mode disables browser credential autofill", () => {
  assert.match(authFormSource, /autoComplete=\{isLogin \? "off" : "on"\}/);
  assert.match(authFormSource, /autoComplete=\{isLogin \? "off" : "email"\}/);
  assert.match(authFormSource, /autoComplete=\{isLogin \? "off" : "new-password"\}/);
});

test("registration confirms passwords and supports explicit password visibility toggles", () => {
  assert.match(authFormSource, /确认密码/);
  assert.match(authFormSource, /password !== confirmPassword/);
  assert.match(authFormSource, /两次输入的密码不一致/);
  assert.match(authFormSource, /aria-label=\{showPassword \? "隐藏密码" : "显示密码"\}/);
  assert.match(authFormSource, /aria-label=\{showConfirmPassword \? "隐藏确认密码" : "显示确认密码"\}/);
});
