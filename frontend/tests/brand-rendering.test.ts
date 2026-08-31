import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const authFormSource = readFileSync(new URL("../components/auth-form.tsx", import.meta.url), "utf8");
const siteNavSource = readFileSync(new URL("../components/site-nav.tsx", import.meta.url), "utf8");

test("login card includes the today-eat icon as a direct static image", () => {
  assert.match(authFormSource, /src="\/brand\/today-eat-icon\.png"/);
  assert.match(authFormSource, /src="\/brand\/today-eat-icon\.png"[\s\S]*?unoptimized/);
});

test("site navigation bypasses image optimization for the today-eat icon", () => {
  assert.match(siteNavSource, /src="\/brand\/today-eat-icon\.png"[\s\S]*?unoptimized/);
});
