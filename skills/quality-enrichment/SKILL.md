---
name: quality-enrichment
description: >
  Audit and uplift the quality of showroom workshops. Works in two modes:
  (1) single-workshop mode on a zt-<slug>-showroom repo (standard OODA layout),
  or (2) monorepo mode on a feature-matrix-driven repo like
  ralf-wiggum-rhoai-kitchen-sink. Validates RAC acceptance criteria against
  actual content, audits screenshots, enriches content with real code examples
  from companion repos, and fixes common quality defects (placeholder tokens,
  vague verify sections, missing callouts, missing transitions). Produces a
  per-workshop structured report. Use when asked to "enrich workshops",
  "quality audit", "uplift workshop content", "validate enrichment",
  "run quality enrichment", "audit kitchen sink", or "fix TODO markers".
triggers:
  keywords:
    - "quality enrichment"
    - "enrich workshops"
    - "quality audit"
    - "uplift workshop"
    - "validate enrichment"
    - "fix TODO markers"
    - "kitchen sink quality"
    - "workshop quality"
  matchMode: any
enabled: true
---

# Quality Enrichment

Audit and uplift the quality of showroom workshops. This skill bridges the gap
between scaffolded content and the quality bar set by the gold-standard workshop
at `~/git/ph-deploy-configure-rhoai/` or `https://github.com/rhpds/ph-deploy-configure-rhoai.git`.

Supports two discovery modes (auto-detected):

| Mode | Trigger | Content path | RAC path |
|------|---------|-------------|----------|
| **Single workshop** | CWD is a `zt-<slug>-showroom` repo, or a slug is passed | `content/modules/ROOT/pages/` | `~/git/zt-<slug>-rac/` |
| **Monorepo** | CWD has `feature-matrix.yml` (e.g., ralf-wiggum) | `features/<category>/<slug>/content/modules/ROOT/pages/` | `rac/<slug>/` |

In single-workshop mode, there is one workshop to process (no batching).
In monorepo mode, the skill loops through all workshops from the matrix.

## Architecture

This skill is an **orchestrator**. It auto-detects the repo layout, builds a
work queue (one item in single-workshop mode, many in monorepo mode), triages
workshops by quality score, then dispatches batches of up to **3 parallel
subagents** to process workshops. Each subagent runs all four enrichment phases
for a single workshop. The orchestrator handles discovery, batch scheduling,
result merging, and the final consolidated report.

```
Orchestrator (this skill)
  |
  +-- Phase 0: Parse feature-matrix.yml, triage, build work queue
  |
  +-- Batch N (up to 3 parallel subagents per batch):
  |     |
  |     +-- Subagent: workshop-enricher(<slug>)
  |           Phase 1: RAC Validation
  |           Phase 2: Screenshot Audit
  |           Phase 3: Code Enrichment
  |           Phase 4: Content Quality Fix
  |           -> per-workshop report JSON
  |
  +-- Phase 5: Merge reports, present consolidated table
```

The orchestrator never modifies content directly -- all fixes happen inside the
subagent for each workshop.

## Skill coordination

- See `skills/docs/WORKSHOP-COMMON-RULES.md` for shared AsciiDoc, image, security,
  and quality rules that define "quality".
- Use **verify-content** (vendored at `skills/verify-content/`) as the quality gate
  after fixes are applied. Run it in headless mode (`ph_payload`) for each workshop.
- Use **workshop-screenshot** patterns (at `skills/workshop-screenshot/`) for
  screenshot gap analysis and capture from a live cluster when one is available.
- Use **openshift-ai-3-3-expert** for RHOAI domain knowledge when enriching
  content or validating commands.
- Use **openshift-4-21-expert** for OpenShift-specific command validation.
- Reference `skills/workshop-act/references/post-enrichment-audit.md` for the
  correctness/deduplication/depth audit methodology used in Phase 4.
- The gold-standard workshop at `~/git/ph-deploy-configure-rhoai/` or
  `https://github.com/rhpds/ph-deploy-configure-rhoai.git` defines what "good"
  looks like: 37 real screenshots, 167 execute blocks, 40 concrete verify
  sections, 182 YAML callout annotations, Apply-Wait-Verify cadence, transition
  prose between every exercise, zero hardcoded product names.

## Prerequisites

Check these before starting. If any are missing, print what is needed and stop.

**Required state (one of):**
- **Single workshop:** CWD is a `zt-<slug>-showroom` repo with
  `content/modules/ROOT/pages/*.adoc`, and a RAC repo exists at
  `~/git/zt-<slug>-rac/`
- **Monorepo:** CWD has a `feature-matrix.yml` with at least one
  `enriched: true` feature (e.g., `~/git/ralf-wiggum-rhoai-kitchen-sink/` or
  `https://github.com/eformat/ralf-wiggum-rhoai-kitchen-sink.git`)

**Required tools:**
- `rg` (ripgrep) -- for fast cross-repo code search (`rg --version`)
- `decided` CLI -- for RAC validation (`decided --version`)
- `git` -- for repo operations

**Optional (for screenshot capture in Phase 2):**
- `oc` CLI authenticated to a live cluster (`oc whoami`)
- `playwright-cli` available
- KUBECONFIG set and cluster accessible

**Enrichment source repos (checked at runtime, not required):**
- `~/git/red-hat-ai-examples/` or `https://github.com/red-hat-data-services/red-hat-ai-examples`
- `~/git/trustyai-llm-demo/` or `https://github.com/trustyai-explainability/trustyai-llm-demo`
- `~/git/llm-on-openshift/` or `https://github.com/rh-aiservices-bu/llm-on-openshift`
- `~/git/agentic-examples/` or `https://github.com/rh-aiservices-bu/agentic-examples`
- `~/git/rhoai-mcp/` or `https://github.com/opendatahub-io/rhoai-mcp`
- `~/git/mlflow-on-rhoai/` or `https://github.com/rh-aiservices-bu/mlflow-on-rhoai`
- `~/git/rhoai-feast-demo/` or `https://github.com/jharmison-redhat/rhoai-feast-demo`
- `~/git/llm-d-deployer/` or `https://github.com/llm-d/llm-d-deployer`

Report which repos are present/missing at startup. Missing repos limit Phase 3
but do not block the other phases.

---

## Workflow

### 0. Detect layout, build work queue, and triage

**0a. Auto-detect layout:**

1. Check CWD for `feature-matrix.yml`. If present → **monorepo mode**.
2. Else check CWD for `content/modules/ROOT/pages/*.adoc`. If present → **single-workshop mode**.
   Derive the slug from the directory name (`zt-<slug>-showroom` → `<slug>`).
3. Else if `$ARGUMENTS` is a slug: check for `~/git/zt-<slug>-showroom/`. If it
   exists → **single-workshop mode** with that repo.
4. Otherwise: ask the user for a path or slug.

**0b. Resolve paths per workshop:**

| Variable | Single workshop | Monorepo |
|----------|----------------|----------|
| `CONTENT_DIR` | `content/modules/ROOT/pages/` | `features/<category>/<slug>/content/modules/ROOT/pages/` |
| `IMAGES_DIR` | `content/modules/ROOT/assets/images/` | `features/<category>/<slug>/content/modules/ROOT/assets/images/` |
| `ANTORA_YML` | `content/antora.yml` | `features/<category>/<slug>/content/antora.yml` |
| `RAC_DIR` | `~/git/zt-<slug>-rac/` | `rac/<slug>/` (relative to monorepo root) |
| `BUILD_CMD` | `make build` | `make build` (from monorepo root) |

**0c. Build work queue:**

- **Monorepo:** parse `feature-matrix.yml`, collect all features where
  `enriched: true`. Accept `$ARGUMENTS` as filters: a single slug, a category
  slug, `--all`, or `--dry-run`.
- **Single workshop:** the queue has exactly one entry (the current workshop).
  `--dry-run` is still accepted.

**0d. Triage scoring:**

For each workshop in the queue, compute a **quality triage score** by scanning
its `CONTENT_DIR`:

| Signal | Points | Detection |
|--------|--------|-----------|
| `// TODO` markers present | +3 | `grep -c '// TODO' pages/*.adoc` |
| Broken heredoc / YAML outside source block | +3 | `cat > ... <<'EOF'` immediately followed by `EOF`, or a stray `----` leaving YAML dangling between source blocks |
| Zero screenshots (only `.gitkeep` in `assets/images/`) | +2 | `find assets/images/ -name '*.png' \| wc -l` == 0 |
| Broken image references | +3 | `image::` refs to non-existent files |
| `<placeholder>` tokens in execute blocks | +2 | `grep -c '<[a-z_]*>' pages/*.adoc` inside source blocks |
| Vague verify sections | +1 | `=== Verify` followed by "completes without error" or "output is displayed" |
| No YAML callouts on manifests | +1 | `[source,yaml]` blocks near `oc apply` without `<1>` markers |
| Missing module summaries | +1 | Pages without `== Module summary` |
| Missing exercise transitions | +1 | Adjacent `== Exercise` headings with no bridging prose |

Sort the work queue by triage score descending (worst quality first).

Report the triage table:

```
=== Quality Triage ===

Slug                          | Category          | Mat | Score | Top Issues
------------------------------+-------------------+-----+-------+---------------------
nemo-guardrails               | guardrails        | GA  | 7     | broken heredocs, placeholders, no screenshots
automated-red-teaming-garak   | evaluation        | GA  | 3     | placeholders, vague verify
kubeflow-trainer-v2           | distributed-train | GA  | 4     | TODOs, no callouts
...

Workshops to process: 29 (of 54 enriched)
Estimated batches: 10 (3 parallel per batch)
```

Ask the user to confirm, or select a subset.

### 1. Batch dispatch

Process workshops in batches of up to 3. For each batch, spawn subagents using
the Agent tool:

```
Agent tool:
  prompt: |
    You are enriching workshop "<slug>".

    WORKSHOP_SLUG: <slug>
    REPO_ROOT: <absolute path to monorepo or showroom repo>
    CONTENT_PATH: <resolved CONTENT_DIR>
    RAC_PATH: <resolved RAC_DIR>
    IMAGES_PATH: <resolved IMAGES_DIR>
    ANTORA_YML: <resolved ANTORA_YML>
    FEATURE_MATURITY: <GA|TP|DP>
    FEATURE_NAME: <name>
    FEATURE_TAGS: <comma-separated tags>
    DRY_RUN: <true|false>
    HAS_CLUSTER: <true|false>
    AVAILABLE_ENRICHMENT_REPOS: <list of confirmed-present repos>

    Run all four phases sequentially. See full instructions below.
    ...
```

Wait for all subagents in the batch to complete before starting the next batch.
Maximum **5 batches** (15 workshops) before pausing for user confirmation.

---

## Subagent: workshop-enricher

Each subagent processes a single workshop through four phases. Phases are
sequential within a workshop because later phases depend on earlier results.

### Phase 1 -- RAC Validation

Read the RAC requirements at `RAC_DIR/requirements/`. For each requirement
file:

1. Parse `[REQ-NNN]` acceptance criteria (lines matching `[REQ-` pattern).
2. For each criterion, search the content pages for evidence it is satisfied:
   - `MUST be able to log in` -> look for `oc login` or console login instructions
   - `MUST deploy` -> look for `oc apply` or `oc create` commands
   - `MUST verify` / `SHOULD observe` -> look for `=== Verify` sections
   - Visual criteria ("MUST see", "observe the dashboard") -> look for `image::` refs
3. Also check `## Verified By` paths in module requirements -- do those files exist?
4. Build an evidence map:

```
| Requirement ID | Criterion | Content Evidence | Status |
|----------------|-----------|------------------|--------|
| RHAIBU-...     | REQ-001 Login | getting-connected.adoc:23 | COVERED |
| RHAIBU-...     | REQ-002 Deploy model | module-02:45 oc apply | COVERED |
| RHAIBU-...     | REQ-003 Query API | module-02:89 curl (vague verify) | PARTIAL |
| RHAIBU-...     | REQ-004 Advanced routing | (none found) | GAP |
```

5. Run `decided validate RAC_DIR/` to check RAC corpus health. Report any
   validation errors but do **not** fix RAC artifacts -- flag them for human attention.

**Output:** RAC evidence map with COVERED / PARTIAL / GAP status per criterion.

### Phase 2 -- Screenshot Audit

Scan the content for screenshot references and validate them:

1. **Find all `image::` references** across all `.adoc` pages.
2. **Check each reference** against actual files in `assets/images/`.
3. **Find TODO screenshot markers**: `// TODO: capture screenshot` or
   `// TODO(screenshot)`.
4. **Check for empty images directory**: only `.gitkeep` present.
5. **Cross-reference** with the Phase 1 evidence map: do RAC criteria that imply
   visual verification have matching screenshots?

Build the screenshot audit:

```
| Image Reference | Page | File Exists | RAC Criterion | Status |
|-----------------|------|-------------|---------------|--------|
| 01-login.png | getting-connected.adoc | NO | REQ-001 | MISSING |
| 02-dashboard.png | module-01.adoc | YES (24KB) | REQ-002 | OK |
| 03-deploy-form.png | module-02.adoc | NO | REQ-003 | MISSING |
```

**If a live cluster is available** (`HAS_CLUSTER: true`), offer to capture missing
screenshots using patterns from `skills/workshop-screenshot/references/capture-patterns.md`.
**Ask the Human before capturing** -- do not auto-capture without confirmation.

**If no cluster**, report the gaps as "needs cluster" and move on.

**Fixes applied (if not dry-run):**
- Remove `// TODO: capture screenshot` comments for screenshots that already exist
  on disk
- Fix broken `image::` references where the filename has a typo but a similar
  file exists in the images directory

### Phase 3 -- Code Enrichment

For workshops that have TODO markers, placeholder tokens, or GAP status from
Phase 1, search the enrichment source repos for real code examples.

**3a. Build a topic-to-repo mapping** from the workshop's tags:

| Tag Pattern | Local Path | Upstream URL | Subdirectory |
|-------------|-----------|--------------|--------------|
| `mcp` | `~/git/rhoai-mcp/` | `https://github.com/opendatahub-io/rhoai-mcp` | -- |
| `evaluation`, `red-teaming` | `~/git/red-hat-ai-examples/` | `https://github.com/red-hat-data-services/red-hat-ai-examples` | `examples/garak-red-teaming/` |
| `evaluation`, `evalhub` | `~/git/red-hat-ai-examples/` | `https://github.com/red-hat-data-services/red-hat-ai-examples` | `examples/agentic-evaluation/` |
| `training`, `fine-tuning` | `~/git/red-hat-ai-examples/` | `https://github.com/red-hat-data-services/red-hat-ai-examples` | `examples/fine-tuning/` |
| `model-serving`, `vllm`, `serving` | `~/git/llm-on-openshift/` | `https://github.com/rh-aiservices-bu/llm-on-openshift` | `llm-servers/vllm/` |
| `guardrails` | `~/git/trustyai-llm-demo/` | `https://github.com/trustyai-explainability/trustyai-llm-demo` | -- |
| `agents` | `~/git/agentic-examples/` | `https://github.com/rh-aiservices-bu/agentic-examples` | -- |
| `mlflow`, `experiment-tracking` | `~/git/mlflow-on-rhoai/` | `https://github.com/rh-aiservices-bu/mlflow-on-rhoai` | -- |
| `feast`, `feature-store` | `~/git/rhoai-feast-demo/` | `https://github.com/jharmison-redhat/rhoai-feast-demo` | -- |
| `llmd`, `distributed-inference` | `~/git/llm-d-deployer/` | `https://github.com/llm-d/llm-d-deployer` | `quickstart/` |
| `ray`, `kuberay` | `~/git/red-hat-ai-examples/` | `https://github.com/red-hat-data-services/red-hat-ai-examples` | `examples/ray/` |
| `model-registry` | `~/git/red-hat-ai-examples/` | `https://github.com/red-hat-data-services/red-hat-ai-examples` | `examples/model-serve-flow/` |
| `automl`, `autorag` | `~/git/red-hat-ai-examples/` | `https://github.com/red-hat-data-services/red-hat-ai-examples` | `examples/automl/` |
| `model-catalog` | `~/git/red-hat-ai-examples/` | `https://github.com/red-hat-data-services/red-hat-ai-examples` | `examples/model-serve-flow/` |

**3b. Search for candidates** using ripgrep:

```bash
rg -l '<search-term>' ~/git/<repo>/ --type py --type yaml --type json --max-depth 4
```

Search terms are derived from:
- The exercise title around the TODO marker
- The RAC acceptance criterion text for GAP items
- The workshop's feature name and description from feature-matrix.yml
- Key resource types (InferenceService, NemoGuardrails, ServingRuntime, etc.)

**3c. Present candidates to the Human.** Never auto-select code examples.

```
Found potential code for "Deploy a model with LLMInferenceService" (REQ-004):

1. ~/git/llm-d-deployer/quickstart/llminferenceservice.yaml
   - LLMInferenceService CR with topology: single-node-default
   - 47 lines, contains apiVersion: inference.llm-d.ai/v1alpha1

2. ~/git/red-hat-ai-examples/examples/model-serve-flow/07_Deployment/deploy-vllm.yaml
   - InferenceService for vLLM (older API, not llm-d)
   - 32 lines

Which should I use? (enter number, or 'skip' to leave as-is)
```

**3d. Embed selected code** (if not dry-run):
- Replace `// TODO(enrichment)` markers with real code blocks
- Replace `<placeholder>` tokens with Antora `{attribute}` references where the
  attribute is defined in the workshop's `antora.yml`
- Add `subs="attributes"` to code blocks that now contain `{...}` references
- For YAML manifests, add as `[source,yaml]` with up to 5 callouts on
  non-obvious fields (see WORKSHOP-COMMON-RULES Section 1a)
- For executable commands, use `[source,bash,role="execute",subs="attributes"]`

### Phase 4 -- Content Quality Fix

Apply mechanical fixes aligned with `WORKSHOP-COMMON-RULES.md` and the
gold-standard patterns from `~/git/ph-deploy-configure-rhoai/` or
`https://github.com/rhpds/ph-deploy-configure-rhoai.git`.

**4a. Broken heredoc restructuring:**

For heredoc blocks where `cat > ... <<'EOF'` is immediately followed by `EOF`
(leaving the YAML dangling outside the source block between two `----`
delimiters): move the closing `EOF` to just before the block's final `----` so
the content sits inside the heredoc, matching the working pattern in the same
workshop's other blocks. While restructuring, strip callout markers (`<1>`,
`<2>`, ...) from heredoc content — they would be copied verbatim into the file
the learner creates and break `oc apply` or Python syntax — and convert any
`<N> *label* -- ...` explanation lists below the block to plain bold-label
prose.

**4b. Placeholder token replacement:**

Scan all execute blocks for angle-bracket tokens like `<model_predictor_url>`,
`<your-model-name>`, `<your-token>`. For each:
- Check if a corresponding Antora attribute exists in `content/antora.yml`
- If yes: replace `<token>` with `{attribute_name}` and add `subs="attributes"`
- If no attribute exists: add the attribute to `antora.yml` with a sensible
  default placeholder, then replace in the content
- If unclear what the attribute should be: flag for human attention

**4c. Verify section concreteness:**

For each `=== Verify` section, check the content:

VAGUE patterns (replace these):
- "The command completes without error"
- "The output is displayed"
- "You should see the result"
- "Check that the resource was created"

CONCRETE replacements:
- After `oc apply`: add `oc wait --for=condition=Ready <resource> --timeout=120s`
  and describe expected output (e.g., "condition met")
- After `curl` to an API: show expected HTTP status code and a representative
  JSON key (e.g., `"status": 200`)
- After `oc get`: show expected column values (e.g., "STATUS shows `Running`,
  READY shows `1/1`")
- After `oc create`: show `oc get <resource> -o name` and expected output

Use the **openshift-ai-3-3-expert** skill for domain-accurate expected outputs.

**4d. YAML callouts (max 5 per block):**

For `[source,yaml]` blocks near `oc apply` / `oc create` commands that have
>3 non-trivial keys (excluding apiVersion, kind, metadata.name,
metadata.namespace) and no existing callout markers:
- Add up to 5 callouts: `# <1>` inline markers + numbered explanations below
- Format: `<1> *Bold label* -- one-sentence explanation.`

**4e. Exercise transitions:**

For adjacent `== Exercise N` headings with no bridging prose between the
previous exercise's `=== Verify` section and the next heading:
- Insert a callback-then-pivot sentence: "Now that you have [done X from
  previous exercise title], you will [do Y from next exercise title]."

**4f. Module summaries:**

For pages missing `== Module summary`:
- Add the standard three-section summary:
  - `**What you accomplished:**` -- 3 past-tense bullets derived from exercise titles
  - `**Key takeaways:**` -- 3 present-tense conceptual bullets
  - `**Next steps:**` -- 1-2 sentence prose linking to the next module

**4g. Missing `subs="attributes"`:**

For `[source,...]` blocks containing `{openshift_`, `{guid}`, `{user}`,
`{password}`, `{rhoai_version}`, or other Antora attribute patterns but
missing `subs="attributes"` on the block header: add it.

**After all Phase 4 fixes**, run `verify-content` in headless mode:

```yaml
ph_payload:
  content_path: <resolved CONTENT_DIR>
  modules: []
  lab_type: workshop
```

If verify-content reports Critical or High findings **introduced by the fixes**,
revert the offending changes and flag for human attention.

---

## Phase 5 -- Merge reports and present

After all batches complete, merge the per-workshop reports into a consolidated
table.

**Summary table:**

```
=== Quality Enrichment Report ===

Slug                        | RAC      | Screenshots | Code      | Quality   | Human
----------------------------+----------+-------------+-----------+-----------+-------
nemo-guardrails             | 5/7 OK   | 0/4 (3 gap) | 3/5 fixed | 6 fixes   | 3
automated-red-teaming-garak | 6/6 OK   | 2/3 (1 gap) | 2/3 fixed | 4 fixes   | 1
kubeflow-trainer-v2         | 4/5 OK   | 0/2 (2 gap) | 1/4 fixed | 5 fixes   | 2
...

Totals:
  Workshops processed: 29
  RAC criteria covered: 142/167 (85%)
  Screenshots present: 24/87 references (28%)
  TODOs resolved: 41/58 (71%)
  Placeholders replaced: 52/68 (76%)
  Quality fixes applied: 89
  Items needing human attention: 34
```

**Items needing human attention**, listed with actionable next steps:

```
=== Human Attention Required ===

1. [nemo-guardrails] RAC gap: REQ-004 (advanced routing) has no content
   -> Add exercise in module-03, or update RAC to remove criterion

2. [nemo-guardrails] Code selection: 2 candidates for guardrails config
   -> ~/git/trustyai-llm-demo/guardrails/config.yaml (NeMo format)
   -> ~/git/red-hat-ai-examples/examples/garak-red-teaming/guardrails/simple.yaml
   -> Pick one and re-run: /quality-enrichment nemo-guardrails

3. [automated-red-teaming-garak] Screenshot: 01-garak-results.png needs cluster
   -> Run with live cluster access when available
```

**Per-workshop report file:** after each workshop's fixes are applied and the
build is verified, write a quality report to
`qa/runs/<slug>/quality.md` in the monorepo (same directory convention as the
functional `fixes.md`): date, triage score before/after, fixes applied, and
items needing human attention. This makes quality progress trackable across
sessions alongside `qa/status.yml` (functional runs).

---

## Guardrails

- **Never auto-select code examples.** Always present candidates and ask the
  Human which to use. Code from enrichment repos may be outdated, wrong version,
  or inappropriate for the workshop's scope.
- **Never modify RAC artifacts.** If a requirement is wrong or a gap is found,
  report it. Only humans update RAC via workshop-orient.
- **Idempotent operation.** Skip workshops that already meet the quality bar
  (triage score == 0). Re-running the skill on an already-fixed workshop should
  produce zero changes.
- **Blast radius containment.** Each subagent operates on exactly one workshop.
  A failure in one workshop does not affect others.
- **Dry-run by default for code enrichment.** Phase 3 code embedding requires
  explicit human confirmation per code example.
- **Preserve existing good content.** Do not rewrite content that already meets
  quality standards. Only fix defects identified by the triage signals.
- **Build validation after fixes.** After each batch completes, run
  `BUILD_CMD` from `REPO_ROOT` to verify Antora still builds. If the build
  fails, revert the batch and report.
- **Maximum 5 batches before pause.** After processing 15 workshops (5 batches
  of 3), pause and ask the user if they want to continue.
- **Security: no secrets.** Follow WORKSHOP-COMMON-RULES Section 0. Never embed
  real credentials, tokens, or internal hostnames. Use `{attribute}` placeholders.
- **Screenshot integrity.** Never fabricate screenshots. Mark missing screenshots
  as gaps. Only capture from a live, verified cluster with human confirmation.
- **ONLY edit files** under the workshop's own content directory
  (`CONTENT_DIR` and `IMAGES_DIR`). Never touch `feature-matrix.yml`, RAC
  artifacts, site playbooks, other workshops' directories, or hub pages.

## Out of scope

- **Scaffolding new workshops** -- use workshop-do (or the ralf-wiggum-loop for monorepo bulk scaffold)
- **Initial enrichment from docs** -- use workshop-do or the ralf-wiggum-loop (Mode 2)
- **RAC creation or modification** -- use workshop-orient
- **Deploying workshops to a cluster** -- use workshop-act
- **Version bumps** -- structural, not quality
- **Cross-workshop navigation** -- handled by the hub component / journey_pass.py
- **Antora playbook or site.yml changes** -- structural, not quality

## Related Skills

- `/verify-content` -- Validate content against Red Hat quality standards
- `/workshop-orient` -- Plan and create RAC requirements
- `/workshop-screenshot` -- Capture screenshots from a live cluster
- `/workshop-act` -- Deploy and test workshops end-to-end
