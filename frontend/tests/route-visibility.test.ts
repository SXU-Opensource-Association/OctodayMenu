import assert from "node:assert/strict";
import test from "node:test";

import { shouldShowSiteNav } from "../lib/route-visibility.ts";

test("authentication routes hide the global navigation", () => {
  assert.equal(shouldShowSiteNav("/auth/login"), false);
  assert.equal(shouldShowSiteNav("/auth/register"), false);
});

test("application routes keep the global navigation", () => {
  assert.equal(shouldShowSiteNav("/"), true);
  assert.equal(shouldShowSiteNav("/canteens"), true);
  assert.equal(shouldShowSiteNav("/restaurants/8"), true);
});
