# asdecided-core CLI Quick Reference

Install: [github.com/asdecided/core/releases](https://github.com/asdecided/core/releases) · also `brew install asdecided/tap/asdecided-core` or `cargo install decided`

## Setup

```bash
decided --version            # verify installation
decided init --key RHAIBU    # initialize repo (creates .decided/config.yaml)
```

## Schema Discovery

```bash
decided schema --list              # list available types: requirement, decision, roadmap, prompt, design
decided schema requirement         # show required/recommended/optional sections
decided schema decision            # show decision artifact structure
decided schema design              # show design artifact structure
decided schema requirement --json  # machine-readable schema
```

Always read the schema before creating an artifact. Never guess field names.

## Creating Artifacts

```bash
decided new requirement ~/git/zt-<slug>-rac/requirements/<slug>.md    # scaffold a requirement
decided new decision ~/git/zt-<slug>-rac/decisions/<slug>.md          # scaffold a decision
decided new design ~/git/zt-<slug>-rac/designs/<slug>.md              # scaffold a design
decided new roadmap ~/git/zt-<slug>-rac/roadmaps/<slug>.md            # scaffold a roadmap
decided new prompt ~/git/zt-<slug>-rac/prompts/<slug>.md              # scaffold a prompt
```

`decided new` mints the artifact ID automatically (e.g., RHAIBU-REQ-001). Never
hand-write or alter the ID.

## Validation

```bash
decided validate ~/git/zt-<slug>-rac/                              # validate all artifacts
decided validate ~/git/zt-<slug>-rac/requirements/<file>.md        # validate single file
decided review ~/git/zt-<slug>-rac/                                # review with prioritized findings
decided review ~/git/zt-<slug>-rac/ --json                         # machine-readable review
decided relationships ~/git/zt-<slug>-rac/ --validate              # check relationship integrity
decided doctor ~/git/zt-<slug>-rac/                                # check repo health
```

Exit codes: 0 = pass, 1 = blocking findings, 2 = usage error.

## Search and Resolution

```bash
decided find "<keywords>" ~/git/zt-<slug>-rac/                     # search for artifacts by content
decided resolve <id> ~/git/zt-<slug>-rac/                          # resolve an artifact ID to its file
```

Use `decided find` to check for duplicates before creating new artifacts.

## Improvement

```bash
decided improve <file>                             # show missing sections with guidance
decided improve <file> --template                  # generate Markdown stubs for missing sections
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

Avoid vague verbs (support, handle, allow, enable) — `decided validate` warns on them.

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

Verify targets resolve before adding: `decided resolve RHAIBU-REQ-001 ~/git/zt-<slug>-rac/`
