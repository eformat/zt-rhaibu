# Capture Patterns Reference

Reusable playwright-cli patterns for capturing OpenShift and RHOAI screenshots.
These patterns were validated against RHOAI 3.3 on OpenShift 4.21 and RHOAI 3.5
on OpenShift 4.x (m6lx9-class cluster, Oct 2026).

## Terminal-Rendered CLI Shots

Raw terminal screenshots (font rendering, window chrome, the operator's prompt
history) are noisy and inconsistent between captures. For exercise steps that
show a CLI command and its expected output, render the REAL captured output as
a terminal-styled HTML page instead — crisp, consistent, and it reads like
exemplar documentation. Validated across 62 screenshots in the RHOAI Operations
workshop (terminal renders for CLI outputs, live captures for browser UI).

**The rule that makes this legitimate:** the text must be the REAL captured
output of the real command on the live cluster — never hand-written or
"expected" output. Only the chrome (window bar, traffic-light dots, colors) is
synthesized. Fabricated output text violates the never-fabricate guardrail.

### Pipeline

1. **Run the real command and capture its output** to a text file:

   ```bash
   oc get datasciencecluster -A > /tmp/term/out02.txt 2>&1
   ```

   Keep the commands that produced each file — the render title quotes them.

2. **Render** with `references/term.py`:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/references/term.py \
     "oc get datasciencecluster -A" /tmp/term/out02.txt /tmp/term/02.html 900
   ```

   Arguments: `<title>` (quoted command + optional outcome note), `<output-file>`,
   `<out-html>`, `[width-px]`. The script applies the terminal chrome (dark
   background, macOS traffic-light dots, green `$ command` line, Red Hat Mono)
   and HTML-escapes everything.

3. **Serve** the render directory over localhost:

   ```bash
   python3 -m http.server 18921 -d /tmp/term &
   ```

4. **Capture** just the terminal box (the `#term` selector excludes the page
   background):

   ```
   playwright-cli -s=workshop-screenshots open http://localhost:18921/02.html
   playwright-cli -s=workshop-screenshots run-code "async page => { await page.waitForLoadState('networkidle'); }"
   playwright-cli -s=workshop-screenshots screenshot "#term" \
     --filename ~/git/zt-<slug>-showroom/content/modules/ROOT/assets/images/02-dsc-ready.png
   ```

5. **Embed** like any other screenshot (deterministic `NN-` filename, verify the
   pixels before embedding).

### Styling details

- **Width:** pass enough px that no line wraps — `term.py` clips overflow
  (`white-space: pre; overflow: hidden`). Wide tables, diffs, and kustomize
  inflation output need 1000–1100; single-command outputs are fine at 900.
- **Titles:** quote the actual command, then a short outcome note in
  parentheses: `"curl POST /maas-api/v1/api-keys (standard tier minted;
  performance tier rejected)"`.
- **Display width** in the AsciiDoc embed: 800 default, 850 for wide renders
  (tables, side-by-side diffs, log dumps).

### Redaction rules for rendered text

- API keys / tokens as short prefixes only: `sk-oai-1ZJqw...` — never a full value.
- Never include passwords, pull secrets, or bearer tokens in rendered output.
- Prefer templated commands (`${HOST}`, `$(oc whoami -t)`) in the quoted command
  line; the rendered output itself should show real values only where they are
  not secret.

## Session Setup

```
playwright-cli -s=workshop-screenshots open <login_url>
```

Use a named session for the entire capture run. This preserves cookies and auth
state between shots.

## Login Flow

### Keycloak / OpenShift OAuth

```
playwright-cli fill '[name="username"]' '<username>'
playwright-cli fill '[name="password"]' '<password>'
playwright-cli click 'button:has-text("Log in")'
playwright-cli run-code "async page => { await page.waitForLoadState('networkidle'); }"
```

After login, save state for reuse:

```
playwright-cli state-save workshop-auth
```

### Restore Auth

```
playwright-cli state-load workshop-auth
```

## RHOAI Dashboard Navigation

### Open RHOAI from OpenShift Console

The RHOAI dashboard opens in a new tab via the app launcher. Use direct URL navigation
instead:

```
playwright-cli open https://rhods-dashboard-redhat-ods-applications.<domain>
playwright-cli run-code "async page => { await page.waitForLoadState('networkidle'); }"
```

Wait for the dashboard to render:

```
playwright-cli run-code "async page => {
  await page.waitForSelector('text=Start by creating your project', { timeout: 15000 });
}"
```

### Navigate to Projects Page

```
playwright-cli click 'a:has-text("Data Science Projects")'
playwright-cli run-code "async page => { await page.waitForLoadState('networkidle'); }"
```

## Project Operations

### Create Project Modal

```
playwright-cli click 'button:has-text("Create project")'
playwright-cli run-code "async page => {
  await page.waitForSelector('[data-testid=\"manage-project-modal\"]', { timeout: 5000 });
}"
playwright-cli screenshot <output_path>
```

### Fill Project Name

```
playwright-cli fill '[data-testid="manage-project-modal-name"]' '<project_name>'
playwright-cli screenshot <output_path>
```

### Submit and Wait for Project Page

```
playwright-cli click '[data-testid="manage-project-modal-submit"]'
playwright-cli run-code "async page => {
  await page.waitForSelector('text=Workbenches', { timeout: 10000 });
}"
playwright-cli screenshot <output_path>
```

## Workbench Lifecycle

### Open Workbench Creation Form

```
playwright-cli click 'button:has-text("Create a workbench")'
playwright-cli run-code "async page => {
  await page.waitForSelector('text=Create workbench', { timeout: 5000 });
}"
playwright-cli screenshot <output_path>
```

### Fill Workbench Name

```
playwright-cli fill '[data-testid="workbench-name"]' '<workbench_name>'
```

### Image Selection Dropdown

```
playwright-cli click '[data-testid="workbench-image-stream-selection"]'
playwright-cli run-code "async page => {
  await page.waitForSelector('[role=\"listbox\"]', { timeout: 5000 });
}"
playwright-cli screenshot <output_path>
```

### Select a Notebook Image

```
playwright-cli click 'button:has-text("Jupyter | Minimal | CPU")'
playwright-cli screenshot <output_path>
```

### Hardware Profile Section

Scroll to the hardware profile section:

```
playwright-cli run-code "async page => {
  const el = await page.waitForSelector('text=Hardware profile');
  await el.scrollIntoViewIfNeeded();
}"
playwright-cli screenshot <output_path>
```

### Cluster Storage Section

```
playwright-cli run-code "async page => {
  const el = await page.waitForSelector('text=Cluster storage');
  await el.scrollIntoViewIfNeeded();
}"
playwright-cli screenshot <output_path>
```

### Submit Workbench Creation

```
playwright-cli click '[data-testid="submit-workbench-button"]'
playwright-cli run-code "async page => { await page.waitForLoadState('networkidle'); }"
```

### Wait for Workbench Startup Phases

Starting state:

```
playwright-cli run-code "async page => {
  await page.waitForSelector('text=Starting', { timeout: 10000 });
}"
playwright-cli screenshot <output_path>
```

Pulling image (expand details):

```
playwright-cli run-code "async page => {
  await page.waitForSelector('text=Pulling', { timeout: 120000 });
}"
playwright-cli screenshot <output_path>
```

Ready state:

```
playwright-cli run-code "async page => {
  await page.waitForSelector('[data-testid=\"notebook-status-text\"]:has-text(\"Running\")', { timeout: 300000 });
}"
playwright-cli screenshot <output_path>
```

### Open JupyterLab

```
playwright-cli click '[data-testid="notebook-route-link"]'
playwright-cli run-code "async page => {
  await page.waitForSelector('.jp-Launcher', { timeout: 30000 });
}"
playwright-cli screenshot <output_path>
```

## Common Waits

### Network Idle

Use after any navigation or form submission:

```
playwright-cli run-code "async page => { await page.waitForLoadState('networkidle'); }"
```

### Animation Settle

Wait 500ms after dynamic content loads for CSS transitions to complete:

```
playwright-cli run-code "async page => { await new Promise(r => setTimeout(r, 500)); }"
```

### Dismiss Transient Warnings

RHOAI sometimes shows brief "There was a problem with the workbench" warnings during
startup. These resolve on their own. If visible when capturing, wait:

```
playwright-cli run-code "async page => {
  const warning = page.locator('text=There was a problem');
  if (await warning.isVisible()) {
    await warning.waitFor({ state: 'hidden', timeout: 30000 });
  }
}"
```

## Screenshot Quality

- Default viewport is 1280x800 — sufficient for most RHOAI dashboard pages
- Capture after `networkidle` and animation settle for clean renders
- Avoid capturing loading spinners — wait for content to appear first
- For long pages, scroll the target section into view before capturing
- Deterministic filenames use 2-digit prefix: `01-`, `02-`, ... `14-`

## Cleanup

```
playwright-cli -s=workshop-screenshots close
```

Remove saved auth state files after the capture run (do not commit them):

```bash
rm -f workshop-auth.json
```
