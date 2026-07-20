---
id: playwright-cli
name: Playwright CLI
description: Automate browser interactions, inspect pages, capture snapshots and screenshots, manage session state, mock requests, and debug or generate Playwright tests with playwright-cli.
triggers:
  keywords:
    - "playwright"
    - "browser automation"
    - "screenshot"
    - "snapshot"
    - "playwright-cli"
    - "e2e test"
    - "end-to-end test"
  extensions:
    - "*.spec.ts"
    - "*.test.ts"
  matchMode: any
enabled: true
---

# Playwright CLI

Use `playwright-cli` for token-efficient browser automation. Prefer snapshots and element refs over screenshots unless the user specifically needs a visual artifact.

## Bootstrap

1. Check whether the CLI is available with `playwright-cli --version`.
2. If the global command is missing, try `npx --no-install playwright-cli --version`.
3. If the CLI is not installed, run `npm install -g @playwright/cli@latest`.
4. If browser binaries are missing, install one with `playwright-cli install-browser chromium`.
5. Use `playwright-cli show` when you want to watch or take over a running browser session.

## Core Workflow

1. Open a browser and navigate to the target page.
2. Capture a snapshot and use refs such as `e12` for interaction.
3. Perform the smallest next action with `click`, `fill`, `press`, `select`, or `eval`.
4. Re-snapshot after meaningful page changes or when state is unclear.
5. Save screenshots, PDFs, traces, or videos only when the user asks for artifacts or when debugging requires them.
6. Close the session, or keep it intentionally with a named session when the workflow spans multiple steps.

## Default Patterns

- Prefer `snapshot` to inspect state; use `screenshot` for visual confirmation only.
- Prefer refs from the snapshot; fall back to CSS selectors or Playwright locators when refs are unstable.
- Use `--raw` when output should feed another shell command or be redirected to a file.
- Use named sessions with `-s=<name>` for parallel tasks or persistent browser state.
- Use `state-save` and `state-load` for authentication reuse.
- Use `console`, `network`, `tracing-start`, and `tracing-stop` when debugging runtime issues.
- Use `run-code` for small one-off Playwright snippets instead of creating a full test file.

## Common Commands

```bash
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli click e15
playwright-cli fill e8 "user@example.com" --submit
playwright-cli press Enter
playwright-cli eval "document.title"
playwright-cli console
playwright-cli network
playwright-cli state-save auth.json
playwright-cli state-load auth.json
playwright-cli screenshot --filename=page.png
playwright-cli tracing-start
playwright-cli tracing-stop
playwright-cli close
```

## Sessions

- Use the default in-memory session for quick checks.
- Use `playwright-cli -s=<name> open <url> --persistent` when the flow needs login persistence across restarts.
- Use `playwright-cli list` to inspect running sessions.
- Use `playwright-cli close-all` for normal cleanup and `playwright-cli kill-all` only for stale or wedged browsers.

### Session Isolation Properties

Each browser session has independent cookies, localStorage, sessionStorage, IndexedDB, cache, browsing history, and open tabs.

### Session Commands

```bash
playwright-cli list                         # list all sessions
playwright-cli close                        # stop default browser
playwright-cli -s=mysession close           # stop a named browser
playwright-cli close-all                    # stop all browsers
playwright-cli kill-all                     # force kill stale processes
playwright-cli delete-data                  # delete default browser data
playwright-cli -s=mysession delete-data     # delete named browser data
```

### Session Best Practices

- Name sessions semantically (e.g., `-s=github-auth`, `-s=docs-scrape`).
- Always clean up sessions when done.
- Keep session names short on macOS to avoid Unix socket path limits.
- Use `--persistent` for login persistence across restarts.

## Guardrails

- Avoid destructive production actions unless the user explicitly wants them.
- Do not guess at hidden page state; re-run `snapshot` when the page may have changed.
- Prefer in-memory sessions unless persistence is required.
- Keep browser actions observable and incremental so failures are easy to diagnose.
- Clean up long-running sessions when they are no longer needed.

---

## Test Generation

Every action you perform with `playwright-cli` generates corresponding Playwright TypeScript code. Collect the generated code into a Playwright test:

```typescript
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('https://example.com/login');
  await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
  await page.getByRole('textbox', { name: 'Password' }).fill('password123');
  await page.getByRole('button', { name: 'Sign In' }).click();
  await expect(page).toHaveURL(/.*dashboard/);
});
```

### Test Generation Best Practices

- Generated code uses role-based locators when possible (more resilient than CSS selectors).
- Take snapshots to understand page structure before recording actions.
- Generated code captures actions but not assertions; add `expect()` calls manually.

---

## Running And Debugging Tests

```bash
# Run all tests
PLAYWRIGHT_HTML_OPEN=never npx playwright test

# Debug a failing test
PLAYWRIGHT_HTML_OPEN=never npx playwright test --debug=cli
# Wait for debugging instructions with session name, then:
playwright-cli attach tw-abcdef
```

Keep the test running in the background while you explore. After fixing, stop the background run and rerun to verify.

---

## Running Custom Code

Use `run-code` for one-off Playwright snippets:

```bash
playwright-cli run-code "async page => {
  await page.waitForLoadState('networkidle');
}"

# Geolocation
playwright-cli run-code "async page => {
  await page.context().grantPermissions(['geolocation']);
  await page.context().setGeolocation({ latitude: 37.7749, longitude: -122.4194 });
}"

# Media emulation
playwright-cli run-code "async page => {
  await page.emulateMedia({ colorScheme: 'dark' });
}"

# File download
playwright-cli run-code "async page => {
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download' }).click();
  const download = await downloadPromise;
  await download.saveAs('./downloaded-file.pdf');
}"

# Page info
playwright-cli run-code "async page => {
  return { title: await page.title(), url: page.url() };
}"
```

---

## Element Attributes

When snapshots don't show `id`, `class`, or `data-*` attributes, use `eval`:

```bash
playwright-cli eval "el => el.id" e7
playwright-cli eval "el => el.className" e7
playwright-cli eval "el => el.getAttribute('data-testid')" e7
playwright-cli eval "el => getComputedStyle(el).display" e7
```

---

## Storage Management

### Save and Restore State

```bash
playwright-cli state-save my-auth-state.json
playwright-cli state-load my-auth-state.json
```

### Cookies

```bash
playwright-cli cookie-list
playwright-cli cookie-list --domain=example.com
playwright-cli cookie-get session_id
playwright-cli cookie-set session abc123 --domain=example.com --httpOnly --secure
playwright-cli cookie-delete session_id
playwright-cli cookie-clear
```

### Local Storage

```bash
playwright-cli localstorage-list
playwright-cli localstorage-get token
playwright-cli localstorage-set theme dark
playwright-cli localstorage-delete token
playwright-cli localstorage-clear
```

### Session Storage

```bash
playwright-cli sessionstorage-list
playwright-cli sessionstorage-get form_data
playwright-cli sessionstorage-set step 3
playwright-cli sessionstorage-delete step
playwright-cli sessionstorage-clear
```

### Security Notes

- Never commit storage state files containing auth tokens.
- Add `*.auth-state.json` to `.gitignore`.
- Delete state files after automation completes.

---

## Request Mocking

```bash
# Mock with status
playwright-cli route "**/*.jpg" --status=404

# Mock with JSON body
playwright-cli route "**/api/users" --body='[{"id":1,"name":"Alice"}]' --content-type=application/json

# Remove headers
playwright-cli route "**/*" --remove-header=cookie,authorization

# List/remove routes
playwright-cli route-list
playwright-cli unroute "**/api/users"
playwright-cli unroute  # remove all
```

### Advanced Mocking with run-code

```bash
# Conditional response
playwright-cli run-code "async page => {
  await page.route('**/api/login', route => {
    const body = route.request().postDataJSON();
    if (body.username === 'admin') {
      route.fulfill({ body: JSON.stringify({ token: 'mock-token' }) });
    } else {
      route.fulfill({ status: 401, body: JSON.stringify({ error: 'Invalid' }) });
    }
  });
}"

# Modify real response
playwright-cli run-code "async page => {
  await page.route('**/api/user', async route => {
    const response = await route.fetch();
    const json = await response.json();
    json.isPremium = true;
    await route.fulfill({ response, json });
  });
}"

# Simulate network failure
playwright-cli run-code "async page => {
  await page.route('**/api/offline', route => route.abort('internetdisconnected'));
}"
```

---

## Tracing

```bash
playwright-cli tracing-start
# ... perform actions ...
playwright-cli tracing-stop
```

Traces capture DOM snapshots, screenshots, network activity, console logs, and timing at each step. Use traces for debugging; use video for demos.

---

## Video Recording

```bash
playwright-cli open
playwright-cli video-start demo.webm
playwright-cli video-chapter "Getting Started" --description="Opening the homepage" --duration=2000
# ... perform actions ...
playwright-cli video-stop
```

### Overlay API for Polished Videos

Use `run-code` with screencast APIs for annotated recordings:

| Method | Use Case |
|--------|----------|
| `page.screencast.showChapter(title, opts)` | Full-screen chapter card with blurred backdrop |
| `page.screencast.showOverlay(html, opts)` | Custom HTML overlay for callouts and highlights |
| `disposable.dispose()` | Remove a sticky overlay |
| `page.screencast.hideOverlays()` / `showOverlays()` | Toggle all overlays |

Overlays are `pointer-events: none` and do not interfere with page interactions.
