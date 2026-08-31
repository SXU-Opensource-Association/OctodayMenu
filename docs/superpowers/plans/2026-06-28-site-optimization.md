# Site Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Implement the accepted P0-P2 usability improvements while preserving mandatory login and existing REST contracts.

**Architecture:** Backend changes are limited to idempotent development seed merging. Frontend rule logic moves into pure tested modules, while UI components consume those rules and existing CRUD APIs; `/admin` uses local resource tabs instead of new routes.

**Tech Stack:** FastAPI, SQLAlchemy, pytest, Next.js 15, React 19, TypeScript, Tailwind CSS, Node test runner.

---

### Task 1: Idempotent Development Data

**Files:**
- Modify: `backend/app/services/dev_seed.py`
- Modify: `backend/tests/test_api.py`
- Modify: `start.sh`

- [x] **Step 1: Write a failing partial-data seed test**

Create one existing area without vendors, run `seed_development_data()` twice, and assert three area types, at least five vendors, at least twelve dishes, no duplicate stable names, and at least one available draw candidate.

- [x] **Step 2: Run the focused backend test**

Run: `cd backend && .venv/bin/pytest tests/test_api.py::test_dev_seed_merges_partial_data_idempotently -q`

Expected: FAIL because the current seed exits when any area exists.

- [x] **Step 3: Implement stable-key seed merging**

Add helpers that get-or-create tags by `(name, category)`, areas by `(area_type, name)`, sections by `(area_id, level)`, vendors by `(area_id, section_id, name)`, and dishes by `(vendor_id, name)`. Populate three area types, five vendors, and twelve sample dishes without overwriting existing values.

- [x] **Step 4: Run seed from the project start script**

After `alembic upgrade head`, execute `.venv/bin/python scripts/seed_dev.py`. Keep failures fatal so the app does not start with an incomplete initialization.

- [x] **Step 5: Verify backend tests**

Run: `cd backend && .venv/bin/pytest -q`

Expected: all tests PASS.

### Task 2: Tested Filtering and Admin Metrics

**Files:**
- Create: `frontend/lib/personalize-rules.ts`
- Create: `frontend/lib/admin-metrics.ts`
- Create: `frontend/tests/personalize-rules.test.ts`
- Create: `frontend/tests/admin-metrics.test.ts`
- Modify: `frontend/package.json`
- Modify: `frontend/components/personalize-panel.tsx`

- [x] **Step 1: Write failing strict-filter tests**

Cover invalid negative/more-than-two-decimal prices, `min > max`, unknown keywords producing zero results, tag and price combinations, matched-dish subsets, and match-reason labels.

- [x] **Step 2: Write failing admin-metric tests**

Build a small `FoodArea[]` fixture and assert active area/vendor/drawable dish counts plus empty-vendor, missing-image, and missing-price counts.

- [x] **Step 3: Run frontend unit tests and verify RED**

Run: `cd frontend && npm test`

Expected: FAIL because the rule modules do not exist.

- [x] **Step 4: Implement pure rule modules**

Export `parsePriceRange()`, `filterVendorResults()`, `clearableFilterDefaults`, and `calculateAdminMetrics()`. Strict filtering must drop all unmatched vendors and return only matching dishes and human-readable reasons.

- [x] **Step 5: Rebuild the personalize panel around tested rules**

Show inline price errors, disable result updates for invalid ranges, add “清空全部条件”, show result reasons, and render only matched dishes.

- [x] **Step 6: Run unit tests and typecheck**

Run: `cd frontend && npm test && npm run typecheck`

Expected: all commands PASS.

### Task 3: Navigation, Login Messaging, and Admin Permission

**Files:**
- Modify: `frontend/components/site-nav.tsx`
- Modify: `frontend/components/user-dashboard.tsx`
- Modify: `frontend/components/admin-dashboard.tsx`

- [x] **Step 1: Add current-route navigation state**

Use `usePathname()` to apply selected styling and `aria-current="page"` to matching navigation links. Keep mobile navigation horizontally scrollable.

- [x] **Step 2: Mark homepage actions as login-only**

Add a compact lock label to the three core action entries while retaining middleware enforcement.

- [x] **Step 3: Fix ordinary-user admin messaging**

Replace “需要管理员登录” with “当前账号没有管理权限”, link back home, and add an action that clears auth before navigating to administrator login.

- [x] **Step 4: Verify typecheck**

Run: `cd frontend && npm run typecheck`

Expected: PASS.

### Task 4: Comment and Like Interaction States

**Files:**
- Modify: `frontend/components/canteen-browser.tsx`

- [x] **Step 1: Add comment validation and feedback**

Disable blank or posting submissions, trim payload text, show `current/1000`, document one-image JPEG/PNG/WebP and 1MB constraints, and scroll the newly inserted comment into view after success.

- [x] **Step 2: Add reply validation and feedback**

Set a 500-character maximum, display count, disable blank/posting replies, keep replies expanded after success, and show a success message.

- [x] **Step 3: Clarify likes and prevent duplicate requests**

Track pending vendor/comment IDs, render “点赞” or “已点赞” plus counts, add distinct aria labels, and disable buttons while requests are active.

- [x] **Step 4: Separate comment and reply totals**

Derive primary and reply totals from the comment tree. Default replies collapsed and provide explicit expand/collapse text.

- [x] **Step 5: Run frontend checks**

Run: `cd frontend && npm test && npm run typecheck`

Expected: PASS.

### Task 5: Management Workspace Tabs, Metrics, and Forms

**Files:**
- Create: `frontend/components/admin/admin-overview.tsx`
- Modify: `frontend/components/admin-dashboard.tsx`
- Modify: `frontend/lib/api.ts`

- [x] **Step 1: Add admin overview**

Render six tested metrics and a blocking alert when `drawableDishCount === 0`. Include last refresh time.

- [x] **Step 2: Add local resource tabs**

Create overview, areas, vendors, dishes, tags, users, and import tabs with a sticky desktop side rail and horizontally scrollable mobile tab row. Render only the active resource section.

- [x] **Step 3: Normalize form state**

For every create/import form, add required labels, dependent disabled inputs, local API error/success messages, and per-form `working` state. Disable submit until required values are valid.

- [x] **Step 4: Add list status controls**

Expose PATCH methods in `api.admin` for areas, vendors, dishes, and tags. Add enable/disable actions to current lists and reload after success.

- [x] **Step 5: Add refresh and user confirmation feedback**

Show refreshing text, success/error feedback, and update timestamp. Require `window.confirm()` before changing a user active state.

- [x] **Step 6: Run frontend tests and build**

Run: `cd frontend && npm test && npm run typecheck && npm run build`

Expected: all commands PASS.

### Task 6: Data Initialization and Browser Acceptance

**Files:**
- Modify: `docs/superpowers/plans/2026-06-28-site-optimization.md`

- [x] **Step 1: Restart with `start.sh`**

Stop the existing script-owned session and run `./start.sh`. Confirm migrations and idempotent seed complete before both servers start.

- [x] **Step 2: Verify data and draw APIs**

Authenticate through the UI, confirm the canteen page has multiple vendors/dishes, and complete a daily draw.

- [x] **Step 3: Verify desktop workflows**

Check strict keyword filtering, invalid price errors, clear-all, comment/reply disabled states, like labels, active navigation, ordinary-user `/admin` messaging, admin overview metrics, tabs, form disabling, and refresh feedback.

- [x] **Step 4: Verify mobile layouts**

Use a mobile viewport for navigation, personalized filtering, comment controls, and admin tabs. Confirm no overlap or horizontal page overflow.

- [x] **Step 5: Run final automated verification**

Run:

```bash
cd backend && .venv/bin/pytest -q
cd frontend && npm test && npm run typecheck && npm run build
```

Expected: zero failures and successful build.
