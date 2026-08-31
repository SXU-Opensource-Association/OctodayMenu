import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const canteenBrowserSource = readFileSync(new URL("../components/canteen-browser.tsx", import.meta.url), "utf8");

test("canteen browser exposes only the three concrete location categories", () => {
  assert.match(canteenBrowserSource, /useState<AreaType>\("CANTEEN"\)/);
  assert.match(canteenBrowserSource, /\["CANTEEN", "SNACK_STREET", "CUSTOM_AREA"\]/);
  assert.doesNotMatch(canteenBrowserSource, /ALL: "全部"/);
});
