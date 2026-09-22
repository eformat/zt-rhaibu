# YAML/Config Callout Guide

**Version**: 1.0  
Reference for annotating non-executable YAML, JSON, and config blocks with AsciiDoc numbered
callouts. Rule C.1 is RECOMMENDED (not mandatory).

---

## C.1 — YAML/Config Callouts

### Syntax

AsciiDoc numbered callouts use inline markers (`# <N>` at line end) paired with explanation
lines below the closing `----`:

```asciidoc
[source,yaml]
----
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: granite-3b                       # <1>
  namespace: rhoai-demo                  # <2>
spec:
  predictor:
    model:
      modelFormat:
        name: vLLM                       # <3>
      runtime: vllm-runtime
      resources:
        limits:
          nvidia.com/gpu: "1"            # <4>
----
<1> *InferenceService name* — used in route URLs and `oc get isvc` lookups.
<2> *Namespace* — must match your project namespace, not `default`.
<3> *Serving runtime* — selects vLLM; other options: `ovms`, `caikit`.
<4> *GPU limit* — this model requires exactly one GPU; setting `0` falls back to CPU.
```

The marker character must match the source language's comment syntax:
- YAML / Python / Shell: `# <N>`
- JSON / Java / Go: `// <N>`

---

## When to Use Callouts

Callouts are **deliberate, not exhaustive**. Use them when all three conditions hold:

1. The block is a **manifest or config the learner applies** to the cluster (`oc apply`,
   `oc create`, `oc process`, `helm install`, `kubectl apply`).
2. The block contains fields the learner **must understand to succeed** in later exercises
   or to debug failures.
3. The field names are **opaque without context** (e.g., `modelFormat.name`, `runtime`,
   `sshAuth`) — a reader cannot guess the right value from the key alone.

### Decision Checklist

Ask yourself before adding callouts:

- Will the learner change this field in a later exercise? → **Yes, callout.**
- Is the field name self-explanatory (`name`, `namespace`, `replicas: 1`)? → **No callout.**
- Is the value a placeholder that Showroom overrides (`{password}`, `{openshift_api_url}`)? → **No callout** — the attribute name is the documentation.
- Does the surrounding prose already explain this field in detail? → **No callout** — avoid duplication.
- Are there more than 5 fields worth annotating? → **Split the block** or callout only the top 5.

---

## When NOT to Use Callouts

| Scenario | Why not |
|---|---|
| Executable shell commands (`[source,role="execute"]`) | Callout markers conflict with the Showroom copy/execute button; the `# <1>` would be copied as part of the command |
| Expected output listings (raw `----` blocks) | Output is read-only context, not something the learner acts on |
| Trivial config (1–2 obvious fields) | Callouts add visual noise with no educational value |
| Blocks where prose explains every field | Duplication — callouts should supplement prose, not repeat it |
| `[source,asciidoc]` examples | Meta-blocks documenting AsciiDoc patterns, not learner-facing config |

---

## Authoring Rules

### Show the file before applying it

When a source file exists on disk (e.g., a manifest the learner will `oc apply -f`),
**always** add an executable `cat` command before the apply so learners can inspect the
full contents:

```asciidoc
. Inspect the InferenceService manifest:
+
[source,bash,role="execute"]
----
cat inferenceservice.yaml
----

Review the key fields:

[source,yaml]
----
spec:
  predictor:
    model:
      runtime: vllm-runtime             # <1>
      resources:
        limits:
          nvidia.com/gpu: "1"            # <2>
----
<1> *Runtime* — must match a ServingRuntime CR that exists in your namespace.
<2> *GPU limit* — set to `0` for CPU-only environments.

. Apply the manifest:
+
[source,bash,role="execute"]
----
oc apply -f inferenceservice.yaml
----
```

The `cat` command is executable (copy/paste into terminal), so the learner sees the
real file contents. The callout block below it highlights the fields that matter — it
can show a trimmed excerpt rather than repeating the entire file. This three-step pattern
(`cat` → callout excerpt → `apply`) gives learners both the full source and the guided
annotation.

Skip the `cat` step only when the YAML is generated inline (e.g., via `cat <<EOF | oc apply -f -`)
or when the content does not originate from a file on disk.

### Maximum 5 callouts per block

More than 5 is noise. If a manifest has many important fields, choose the top 5 by asking:
"Which fields will trip up a learner who gets them wrong?" The rest can be covered in prose.

### One sentence per callout

Each explanation is a single sentence — concise and scannable. Never a paragraph.

### Bold label, then em-dash

Lead with the field name in bold, then an em-dash and the explanation:

```
<1> *Runtime* — selects the vLLM serving runtime for this InferenceService.
```

Not:
```
<1> The runtime field selects which serving runtime the InferenceService will use,
    in this case vLLM, which is an open-source high-throughput inference engine.
```

### Numbering is sequential

Markers must be sequential (`<1>`, `<2>`, `<3>`) and match exactly between the inline
markers and the explanation list. A mismatch produces an Antora build warning and renders
incorrectly.

---

## Attribute Substitution + Callouts

When a YAML block contains both `{attribute}` placeholders and callout markers, you need
both `subs` values:

```asciidoc
[source,yaml,subs="attributes,callouts"]
----
apiVersion: v1
kind: Secret
metadata:
  name: maas-api-key                     # <1>
  namespace: {project_name}              # <2>
stringData:
  api-key: "{maas_api_key}"             # <3>
----
<1> *Secret name* — referenced by the InferenceService's `envFrom` mount.
<2> *Namespace* — injected from the Showroom `project_name` attribute.
<3> *API key* — injected at deploy time; never hardcode a real key.
```

Without `subs="attributes,callouts"`:
- Missing `attributes` → `{project_name}` renders literally.
- Missing `callouts` → `<1>` renders literally as text, not as a circled number.

Plain `[source,yaml]` without `subs` works only when the block has callouts but no
`{attribute}` placeholders.

---

## Bad/Good Examples

### Bad: Over-annotated (every field has a callout)

```asciidoc
[source,yaml]
----
apiVersion: v1              # <1>
kind: ConfigMap             # <2>
metadata:
  name: app-config          # <3>
  namespace: demo           # <4>
data:
  LOG_LEVEL: info           # <5>
  DB_HOST: postgres.svc     # <6>
  DB_PORT: "5432"           # <7>
----
<1> API version for ConfigMap resources.
<2> The Kubernetes resource kind.
<3> Name of the ConfigMap.
<4> Target namespace.
<5> Application log level.
<6> Database hostname.
<7> Database port.
```

**Problem**: `apiVersion`, `kind`, `metadata.name`, and `metadata.namespace` are
self-explanatory Kubernetes boilerplate. Seven callouts overwhelm the reader. The learner
cannot tell which fields are actually important.

### Good: Focused on what matters

```asciidoc
[source,yaml]
----
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: demo
data:
  LOG_LEVEL: info           # <1>
  DB_HOST: postgres.svc     # <2>
----
<1> *Log level* — set to `debug` in Exercise 4 to trace query plans.
<2> *Database host* — must match the Service name from Exercise 1; a wrong value causes `ECONNREFUSED`.
```

**Why this works**: Only the two fields the learner will interact with or troubleshoot are
callout-annotated. The Kubernetes boilerplate is left clean.

### Bad: Callouts on an executable block

```asciidoc
[source,role="execute"]
----
oc apply -f inferenceservice.yaml  # <1>
oc wait --for=condition=Ready isvc/granite-3b --timeout=120s  # <2>
----
<1> Applies the manifest.
<2> Waits for readiness.
```

**Problem**: The `# <1>` markers will be copied into the terminal by the Showroom
execute button, causing shell syntax errors. Executable blocks must never have callouts.

### Good: Callout on the manifest, not the command

```asciidoc
Review the InferenceService manifest before applying it:

[source,yaml]
----
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: granite-3b
spec:
  predictor:
    model:
      runtime: vllm-runtime             # <1>
----
<1> *Runtime* — must match a ServingRuntime CR that exists in your namespace.

. Apply the manifest:
+
[source,role="execute"]
----
oc apply -f inferenceservice.yaml
----
```

---

## Real-World Exemplar

From `zt-playground-create-showroom/content/modules/ROOT/pages/module-04-viewcode.adoc`:

```asciidoc
[source,python]
----
from llama_stack_client import LlamaStackClient  # <1>

client = LlamaStackClient(base_url=LLAMA_STACK_URL)  # <2>

model_name = "maas-vllm-inference-1/qwen38-27b"  # <3>
...
response = client.responses.create(**config)  # <4>
----
<1> *Import* — the `llama_stack_client` Python package provides the SDK
<2> *Client instantiation* — `LlamaStackClient` connects to the Llama Stack server URL
<3> *Model name* — matches the model you selected in Module 2 (`{model_name}`)
<4> *Create call* — `client.responses.create()` is the programmatic equivalent of clicking Send
```

This exemplar shows the pattern applied to Python (non-executable, read-only code review).
The same pattern works identically for YAML, JSON, or any `[source,<lang>]` block.

---

## Quick Reference

| Aspect | Rule |
|---|---|
| When | Manifest applied to cluster + opaque fields + learner needs to understand |
| When not | Execute blocks, output listings, trivial config, prose already covers it |
| Max callouts | 5 per block |
| Format | `<N> *Bold label* — one sentence.` |
| Subs | `[source,yaml,subs="attributes,callouts"]` when both are needed |
| Numbering | Sequential, matching between inline and explanation list |
