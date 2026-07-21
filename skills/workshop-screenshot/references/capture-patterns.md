# Capture Patterns Reference

Reusable playwright-cli patterns for capturing OpenShift and RHOAI screenshots.
These patterns were validated against RHOAI 3.3 on OpenShift 4.21.

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
