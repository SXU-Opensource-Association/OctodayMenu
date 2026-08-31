# Project Start Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Add a root-level shell script that safely starts, monitors, and stops the FastAPI and Next.js development servers for local and LAN access.

**Architecture:** `start.sh` performs deterministic prerequisite and port checks, runs Alembic migration synchronously, then owns both long-running child processes. Signal traps and child-exit monitoring guarantee that processes started by the script are cleaned up together.

**Tech Stack:** Bash 3.2-compatible shell, macOS/Linux command-line utilities, FastAPI/Uvicorn, Next.js/npm.

---

### Task 1: Script Contract and Failure Paths

**Files:**
- Create: `tests/test_start_script.sh`
- Create: `start.sh`

- [x] **Step 1: Write the failing shell contract test**

The test must assert that `start.sh` exists, passes `bash -n`, contains `set -Eeuo pipefail`, checks ports 3000/8000, runs `alembic upgrade head`, starts Uvicorn on `0.0.0.0:8000`, starts `npm run dev`, and installs cleanup traps.

- [x] **Step 2: Run the test and verify RED**

Run: `bash tests/test_start_script.sh`

Expected: FAIL because `start.sh` does not exist.

- [x] **Step 3: Implement prerequisite and port checks**

Create `start.sh` with a project-root resolver, `require_file`, `require_command`, and `port_in_use` helpers. Validate `.env`, virtualenv executables, npm, frontend dependencies, and both ports before starting.

- [x] **Step 4: Implement migration, process ownership, and cleanup**

Run Alembic before starting services. Store backend/frontend PIDs, trap `INT TERM EXIT`, terminate only those PIDs, and use `wait -n` where available with a Bash 3.2-compatible polling fallback.

- [x] **Step 5: Run contract and syntax tests**

Run: `bash tests/test_start_script.sh && bash -n start.sh`

Expected: both commands exit 0.

### Task 2: Runtime Verification and Documentation

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/plans/2026-06-27-project-start-script.md`

- [x] **Step 1: Verify occupied-port safety**

With existing services on 3000/8000, run `./start.sh`.

Expected: nonzero exit with a port-occupied message; existing service PIDs remain alive.

- [x] **Step 2: Stop existing development sessions and run the script**

Run: `./start.sh`.

Expected: migration succeeds, both services start, and local/LAN URLs are printed.

- [x] **Step 3: Verify application health**

Run curl with proxy bypass against localhost and the detected LAN IP:

```bash
curl --noproxy '*' -fsS http://127.0.0.1:3000/api/health
curl --noproxy '*' -fsS "http://${LAN_IP}:3000/auth/register"
```

Expected: health JSON and HTTP 200.

- [x] **Step 4: Verify signal cleanup**

Send `INT` to the foreground script and assert that processes it started no longer listen on ports 3000/8000.

- [x] **Step 5: Document usage**

Add root README commands:

```bash
chmod +x start.sh
./start.sh
```

Explain prerequisite setup, port behavior, displayed LAN URL, and `Ctrl+C` cleanup.

- [x] **Step 6: Run final verification**

Run:

```bash
bash tests/test_start_script.sh
cd frontend && npm run typecheck
```

Expected: all commands exit 0.
