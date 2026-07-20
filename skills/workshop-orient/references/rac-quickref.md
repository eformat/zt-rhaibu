# rac-core CLI Quick Reference

## Setup

```bash
source .venv/bin/activate
rac --version            # verify installation
rac init --key RHAIBU    # initialize repo (creates .~/git/zt-<slug>-rac/config.yaml)
```

## Schema Discovery

```bash
rac schema --list              # list available types: requirement, decision, roadmap, prompt, design
rac schema requirement         # show required/recommended/optional sections
rac schema decision            # show decision artifact structure
rac schema design              # show design artifact structure
rac schema requirement --json  # machine-readable schema
```

Always read the schema before creating an artifact. Never guess field names.

## Creating Artifacts

```bash
rac new requirement ~/git/zt-<slug>-rac/requirements/<slug>.md    # scaffold a requirement
rac new decision ~/git/zt-<slug>-rac/decisions/<slug>.md          # scaffold a decision
rac new design ~/git/zt-<slug>-rac/designs/<slug>.md              # scaffold a design
rac new roadmap ~/git/zt-<slug>-rac/roadmaps/<slug>.md            # scaffold a roadmap
rac new prompt ~/git/zt-<slug>-rac/prompts/<slug>.md              # scaffold a prompt
```

`rac new` mints the artifact ID automatically (e.g., RHAIBU-REQ-001). Never
hand-write or alter the ID.

## Validation

```bash
rac validate ~/git/zt-<slug>-rac/                              # validate all artifacts
rac validate ~/git/zt-<slug>-rac/requirements/<file>.md        # validate single file
rac review ~/git/zt-<slug>-rac/                                # review with prioritized findings
rac review ~/git/zt-<slug>-rac/ --json                         # machine-readable review
rac relationships ~/git/zt-<slug>-rac/ --validate              # check relationship integrity
rac doctor ~/git/zt-<slug>-rac/                                # check repo health
```

Exit codes: 0 = pass, 1 = blocking findings, 2 = usage error.

## Search and Resolution

```bash
rac find "<keywords>" ~/git/zt-<slug>-rac/                     # search for artifacts by content
rac resolve <id> ~/git/zt-<slug>-rac/                          # resolve an artifact ID to its file
```

Use `rac find` to check for duplicates before creating new artifacts.

## Improvement

```bash
rac improve <file>                             # show missing sections with guidance
rac improve <file> --template                  # generate Markdown stubs for missing sections
```

## Requirement Syntax

Requirements use normative wording under `## Requirements`:

```markdown
## Requirements

- [REQ-001] Learner MUST be able to log into the OpenShift console
- [REQ-002] Learner MUST deploy a model using RHOAI model serving
- [REQ-003] Learner SHOULD query the model via REST API
- [REQ-004] Learner MAY configure autoscaling for the inference service
```

Avoid vague verbs (support, handle, allow, enable) — `rac validate` warns on them.

## Relationships

Link artifacts using `## Related <Type>` sections:

```markdown
## Related Requirements

- RHAIBU-REQ-001

## Related Decisions

- RHAIBU-DEC-001
```

Use bare artifact IDs only — no descriptive suffixes. The relationship resolver
matches the full line text against the identifier index.

Verify targets resolve before adding: `rac resolve RHAIBU-REQ-001 ~/git/zt-<slug>-rac/`
