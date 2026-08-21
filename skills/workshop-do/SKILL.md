---
name: workshop-do
description: >
  Scaffold workshop content and infrastructure code from RAC requirements. Produces
  two separate repos: (1) a zt-<slug>-showroom Antora/AsciiDoc content repo following
  the ai-lightning-wordswarm-showroom pattern, and (2) a zt-<slug>-automation GitOps
  infrastructure repo following the ai-lightning-labs-automation 3-layer ArgoCD
  app-of-apps pattern. Use when someone wants to "scaffold a workshop", "generate
  workshop code", "build workshop content", "create showroom content", "create workshop
  infrastructure", "implement the workshop", "write the workshop code", "antora
  scaffold", "showroom scaffold", "gitops workshop", "helm charts for workshop", or
  "workshop implementation". This is the third step of the OODA workshop pipeline
  (Observe -> Orient -> Do -> Act). Do NOT use for analyzing demos (workshop-observe),
  planning workshops (workshop-orient), or deploying/testing (workshop-act).
triggers:
  keywords:
    - "workshop do"
    - "scaffold workshop"
    - "workshop content"
    - "workshop infrastructure"
    - "showroom scaffold"
    - "workshop implementation"
    - "ooda do"
    - "generate workshop"
  matchMode: any
enabled: true
---

# Workshop Do

Scaffold two codebases from RAC requirements: a content repo and an infrastructure repo.

## Skill coordination

- **Delegate content scaffolding** to the `openshift-workshop-builder` skill. It owns
  the Antora/showroom structure, file templates, AsciiDoc patterns, and build process.
  This skill orchestrates it with the right parameters, then adds workshop-specific content.
- Use the **OpenShift 4.21 Expert** skill for OpenShift-specific lab steps.
- Use the **OpenShift AI 3.3 Expert** skill for RHOAI-specific lab steps.
- Reference `https://github.com/rhpds/ai-lightning-wordswarm-showroom` as the content exemplar.
- Reference `https://github.com/rhpds/ai-lightning-labs-automation` as the infrastructure exemplar.
- Infrastructure patterns are documented in `${CLAUDE_SKILL_DIR}/references/infra-patterns.md`.
- See `skills/docs/WORKSHOP-COMMON-RULES.md` for shared AsciiDoc, image, security,
  and quality rules.

## Prerequisites

Check these before starting. If any are missing, print what's needed and stop.

**Required tools:**
- `git` — `git --version`
- `node` / `npm` — `node --version && npm --version` (for Antora build)
- `helm` — `helm version --short` (for chart validation)
- `decided` CLI — `decided --version` ([install](https://github.com/asdecided/core/releases))

**Required exemplar repos** (clone if missing):
- Content exemplar: `https://github.com/rhpds/ai-lightning-wordswarm-showroom`
  ```bash
  git clone https://github.com/rhpds/ai-lightning-wordswarm-showroom.git https://github.com/rhpds/ai-lightning-wordswarm-showroom
  ```
- Infrastructure exemplar: `https://github.com/rhpds/ai-lightning-labs-automation`
  ```bash
  git clone https://github.com/rhpds/ai-lightning-labs-automation.git https://github.com/rhpds/ai-lightning-labs-automation
  ```

**Required state:**
- A workshop RAC repo at `~/git/zt-<slug>-rac/` (from workshop-orient) containing:
  requirements with acceptance criteria, decisions, and at least one design with a
  parameter inventory

## Workflow

### 1. Read RAC requirements

Accept `$ARGUMENTS` as a workshop slug. If no argument is provided, discover
existing RAC repos:

```bash
ls -d ~/git/zt-*-rac/ 2>/dev/null
```

If exactly one exists, use it. If multiple exist, list them and ask the user to
choose. If none exist, stop — workshop-orient must be run first.

The RAC repo is at `~/git/zt-<slug>-rac/`.
Read all requirement artifacts from `~/git/zt-<slug>-rac/requirements/`. Extract:
- Module list with ordering
- Acceptance criteria per module
- Parameter inventory from the design artifact
- Infrastructure requirements (operators, CRDs, GPUs, storage)

### 2. Determine output locations

Create two sibling repos in `~/git/`:
- Content: `~/git/zt-<slug>-showroom/`
- Infra: `~/git/zt-<slug>-automation/`

Confirm the slug and output paths with the user before creating directories.

### 3. Scaffold the content repo

Follow the `openshift-workshop-builder` workflow to create the showroom structure:

**Required files** (all must exist for `make build` to succeed):

- `package.json` — Antora dependencies (`@antora/cli`, `@antora/site-generator`)
- `Makefile` — use this exact template (matches `zt-workbench-create-showroom`):
    ```makefile
    PORT ?= 8887
    DOCS_DIR := $(shell pwd)
    SITE_DIR := $(DOCS_DIR)/www

    .PHONY: install build serve clean

    install:
    	cd $(DOCS_DIR) && npm install

    build: install
    	rm -rf $(SITE_DIR)
    	cd $(DOCS_DIR) && npx antora site.yml --stacktrace
    	touch $(SITE_DIR)/.nojekyll

    serve: build
    	@echo "Serving at http://localhost:$(PORT)"
    	python3 -m http.server $(PORT) --directory $(SITE_DIR)

    clean:
    	rm -rf $(SITE_DIR)
    ```
    Key rules: port 8887 (not 8080), output to `www/` (not `docs/`), call `npx antora`
    directly (not via `npm run`), `rm -rf` before each build for clean output,
    `python3 -m http.server` for serve, `.nojekyll` required for GitHub Pages.
- `site.yml` — Antora playbook. MUST use the RHDP theme bundle — never the Antora
    default. Copy this block exactly:
    ```yaml
    ui:
      bundle:
        url: https://github.com/rhpds/rhdp_showroom_theme/releases/download/summit-2026/ui-bundle.zip
        snapshot: true
      supplemental_files: ./content/supplemental-ui
    asciidoc:
      attributes:
        showroom-collection-version: v1.5.2
    antora:
      extensions:
        - require: ./content/lib/inject-buttons.js
    output:
      dir: ./www
    ```
    Output MUST be `./www` — the gh-pages workflow uploads `path: www`, and the
    Makefile `SITE_DIR` must match.
- `content/antora.yml` — component descriptor with all `{attribute}` defaults from
  the RAC parameter inventory
- `content/modules/ROOT/nav.adoc` — navigation tree with entries for each module
- `.gitignore` — exclude `node_modules/`, `www/`, `.cache/` (not `docs/` — output is `www/`)
- `content/supplemental-ui/css/site-extra.css` — image shadow + send-to button styles
- `content/supplemental-ui/js/buttons.js` — send-to-terminal JS
- `content/supplemental-ui/img/favicon.svg` — Red Hat favicon
- `content/supplemental-ui/partials/head-meta.hbs` — injects CSS + Font Awesome
- `content/supplemental-ui/partials/head-icons.hbs` — favicon link
- `content/lib/inject-buttons.js` — Antora extension (inlines CSS/JS per page)

  **Copy** `content/supplemental-ui/` and `content/lib/` from an existing workshop
  showroom (e.g., `~/git/zt-workbench-create-showroom/`) — do not recreate from
  scratch and do not use a generic Antora UI bundle.

**Content pages** under `content/modules/ROOT/pages/`:

- `index.adoc` — welcome page with: title, what you'll learn, who this is for,
  prerequisites, estimated time, link to first module
- `getting-connected.adoc` — login steps using `{user}` / `{password}` attributes,
  project setup, environment verification
- `NN-module-MM-<slug>.adoc` — one page per module requirement, with:
  - `:navtitle:` and `:toc: macro` attributes
  - `== Learning objectives` section (bulleted list from RAC requirement)
  - Numbered `== Exercise N: Title` sections with `[source,role="execute"]` code blocks
  - `=== Verify` section after each exercise
  - `== Module summary` with key takeaways
- `NN-conclusion.adoc` — wrap-up with per-module summary, resources, thank you

**AsciiDoc rules:**
- Every command uses `[source,role="execute"]` for the Showroom copy/execute button
- Use `[source,bash,role="execute",subs="attributes"]` for blocks containing `{attribute}` values
- Use `{attribute}` substitution for all environment-specific values — never hardcode
- Page naming: `NN-descriptive-name.adoc` with 2-digit prefix for ordering

**Optional files** (add if the workshop needs interactive features):
- `ui-config.yml` — showroom tabs and terminal configuration

**Always include** (copy from exemplar `gpu-resource-mgmt-showroom`):
- `.github/workflows/gh-pages.yml` — GitHub Pages CI/CD. Triggers on pushes to
  `content/**`, `site.yml`, or the workflow file itself. Builds with Antora (Node 22),
  overrides the UI bundle to the `showroom-template` release for gh-pages rendering,
  uploads `www/` as the pages artifact, and deploys on merge to `main`. PRs run the
  build step only (no deploy). Copy verbatim — do not recreate.

### 4. Initialize content repo and test build

```bash
cd ../zt-<slug>-showroom
git init && git add -A && git commit -m "Initial workshop scaffold"
npm install
make build
```

Verify the build succeeds. Antora requires at least one git commit — without it the
site builds but contains zero pages. If the build fails, fix errors and retry.

### 5. Scaffold the infrastructure repo

Read `${CLAUDE_SKILL_DIR}/references/infra-patterns.md` for the exact template patterns.

Follow the `ai-lightning-labs-automation` 3-layer architecture:

```
zt-<slug>-automation/
  bootstrap.yaml                   ← root app-of-apps entry point
  cluster/
    infra/
      bootstrap/
        Chart.yaml
        values.yaml
        templates/
          appproject-infra.yaml
          appproject-platform.yaml
          appproject-tenants.yaml
          application-bootstrap-platform.yaml
          configmap-cluster-provisiondata.yaml
          application-<workload>.yaml  (one per infra workload)
    platform/
      bootstrap/
        Chart.yaml
        values.yaml
        templates/
          application-<workload>.yaml  (one per platform workload)
      <workload>/                      (individual workload charts)
        Chart.yaml
        values.yaml
        templates/
  tenant/
    bootstrap/
      Chart.yaml
      values.yaml
      templates/
        application-<workload>.yaml  (one per tenant workload)
    <workload>/
      Chart.yaml
      values.yaml
      templates/
```

**Key patterns to follow:**

1. **Root app-of-apps entry point** — create `bootstrap.yaml` at the repo root.
   This is a single ArgoCD Application pointing to `cluster/infra/bootstrap/` with
   `deployer.domain` and `deployer.apiUrl` as `REPLACE_ME` placeholders. Applying
   this one file to the cluster kicks off the entire cascade:
   ```
   bootstrap.yaml → infra/bootstrap (AppProjects + workload Apps + platform App)
                       → platform/bootstrap (platform workload Apps)
                       → tenant/bootstrap (per-user Apps)
   ```
   In the exemplar, the Ansible role `ocp4_workload_gitops_bootstrap` creates this
   entry-point dynamically. We provide a static YAML so it can be applied standalone.

2. **YAML anchors** at the top of every `values.yaml`:
   ```yaml
   default_settings: &git_defaults
     repoURL: https://github.com/<org>/zt-<slug>-automation
     targetRevision: main
   ```

3. **Workload blocks** — each with `enabled: true/false` and `git:` using `<<: *git_defaults`

4. **Application templates** — gated by `{{ if .Values.<key>.enabled }}`, with standard
   syncPolicy (automated, CreateNamespace, retry 10/5s/2x/3m)

5. **Cross-layer wiring** — infra creates `bootstrap-platform` Application that forwards
   `deployer` and `platformValues` via `helm.values` with `toYaml | nindent`

6. **Tenant templates** — append `{{ .Values.tenant.name }}` to Application names,
   forward `deployer`, `tenant`, and workload-specific values

### 6. Create workshop-specific workload charts

Based on infrastructure requirements from RAC:

- **Operator subscriptions** (infra layer): e.g., RHOAI operator, GPU operator.
  Each is a minimal chart with a Subscription CR template.
- **Platform configurations** (platform layer): e.g., DataScienceCluster CR,
  ServingRuntime CRs, InferenceService templates, namespace setup.
  **Important:** DataScienceCluster CRs MUST use `apiVersion: datasciencecluster.opendatahub.io/v2`.
  The v1 API is rejected when v2-only components (mlflowoperator, trainer, etc.) exist.
  Include all v2 components in the template (dashboard, workbenches, aipipelines,
  kserve, modelregistry, ray, trustyai, kueue, trainingoperator, trainer,
  mlflowoperator, feastoperator, llamastackoperator) — set unused ones to `Removed`.
- **Tenant resources** (tenant layer): e.g., per-user namespaces, workbenches,
  RBAC bindings, secrets.

Each workload chart follows:
```
<workload-name>/
  Chart.yaml        # name, version, description
  values.yaml       # defaults (deployer block, workload-specific)
  templates/
    <resource>.yaml  # one template per K8s resource
```

### 7. Validate and report

```bash
decided validate ~/git/zt-<slug>-rac/
```

Confirm requirements still pass. Print a summary:
- Files created in content repo (count by type: .adoc, .yaml, .json, .yml)
- Files created in infra repo (count by layer)
- Content build status (pass/fail)
- Helm chart validation (run `helm lint` on each chart)

Prompt: "Workshop scaffolded. Run `/workshop-act` to deploy and test on the prelude cluster."

## Guardrails

- Never hardcode cluster-specific values in content. Use `{attribute}` substitution.
- Never hardcode cluster-specific values in infra. Use `deployer.*` and helm values.
- Follow the `openshift-workshop-builder` patterns exactly for content structure.
- Follow the `ai-lightning-labs-automation` patterns exactly for infrastructure.
- Every command in a module must use `[source,role="execute"]` blocks.
- Keep Helm charts minimal — one chart per logical workload.
- Initialize git before running `make build` — Antora requires at least one commit.
- Do not create screenshots — that requires a running cluster and is deferred to
  `workshop-act`.

## Out of scope

- Screenshot capture (requires a running cluster — deferred to workshop-act)
- Deployment to a cluster (workshop-act)
- Workshop planning or requirement gathering (workshop-orient)
- Analyzing demo applications (workshop-observe)

## Related Skills

- `/workshop-orient` — Plan the workshop and create RAC requirements
- `/workshop-act` — Deploy and test the workshop end-to-end
- `/workshop-screenshot` — Capture and embed screenshots into content
- `/openshift-workshop-builder` — AsciiDoc/Antora scaffolding patterns
- `/showroom:verify-content` — Validate content against Red Hat quality standards
