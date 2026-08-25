# zt-rhaibu — OODA Workshop Factory

Workshop creation pipeline based on the OODA loop. Each phase is a skill in `skills/`.

## Pipeline

```
Observe → Orient → Do → Act
(images)   (RAC)   (code)  (deploy+test)
```

**Each workshop gets its own RAC repo** at `~/git/zt-<slug>-rac/` — the planning contract between phases.

| Phase | Skill | Input | Output |
|-------|-------|-------|--------|
| Observe | `workshop-observe` | Demo screenshots/keyframes | `~/git/zt-<slug>-rac/assets/observations-<slug>.md` |
| Orient | `workshop-orient` | Observation doc or freeform | `~/git/zt-<slug>-rac/requirements/`, `decisions/`, `designs/` |
| Do | `workshop-do` | RAC artifacts | `~/git/zt-<slug>-showroom/` + `~/git/zt-<slug>-automation/` |
| Act | `workshop-act` | Scaffolded repos + RAC requirements | Deployed workshop on prelude cluster |

Three repos per workshop: `zt-<slug>-rac/`, `zt-<slug>-showroom/`, `zt-<slug>-automation/`.
This factory repo (`zt-rhaibu`) holds only skills and tooling — no per-workshop state.

## Exemplar Repos

- **Content**: https://github.com/rhpds/ai-lightning-wordswarm-showroom — Antora/AsciiDoc showroom pattern
- **Infra**: `zt-showroom-deployer` Helm chart (source at `~/git/zt-showroom-deployer/`, published as `eformat/showroom-deployer` at https://eformat.github.io/helm-charts) — the per-workshop `zt-<slug>-automation` repo is a thin `values-<slug>.yaml` + `Makefile` wrapper around it (no ArgoCD app-of-apps)

## Skill Coordination

- **openshift-workshop-builder** — handles Antora/showroom content scaffolding (called by workshop-do)
- **playwright-cli** — browser automation for testing (called by workshop-act)
- **openshift-4-21-expert** — OpenShift console flows and cluster admin steps
- **openshift-ai-3-3-expert** — RHOAI workbenches, model serving, pipelines
- **verify-content** (`/verify-content`) — validates showroom content against Red Hat quality standards; quality gate in workshop-act. Vendored from the RHDP skills marketplace and registered as a slash command.
- **catalog-builder** (`/catalog-builder`) — builds an RHDP AgnosticV catalog entry at publish time. Vendored from the RHDP skills marketplace and registered as a slash command.

## RAC

Requirements As Code via [`asdecided-core`](https://github.com/asdecided/core/releases). Assumes `decided` is on PATH.

Artifact ID prefix: `RHAIBU-`. Key CLI commands: `decided schema`, `decided new`, `decided validate`, `decided review`, `decided relationships`.

Each workshop's RAC lives in its own repo (`~/git/zt-<slug>-rac/`), not in this factory repo.
Skills scaffold the RAC repo with `decided init --key RHAIBU` during Observe/Orient.

In the workshop RAC a full set of folders could include:

```bash
mkdir -p ~/git/zt-<slug>-rac/assets rac/decisions ~/git/zt-<slug>-rac/designs ~/git/zt-<slug>-rac/prompts ~/git/zt-<slug>-rac/requirements ~/git/zt-<slug>-rac/roadmaps
```

## Future

Skills will integrate with hermes kanban for independent step/stage processing with LLM-as-judge validation.
