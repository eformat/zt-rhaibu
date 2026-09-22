# Documentation Grounding Reference

Actionable guide for grounding workshop content in product documentation.
See WORKSHOP-COMMON-RULES.md Section 10 for the governing rules (G.1–G.4).

---

## Extraction Workflow

1. **Locate product PDFs** for the target RHOAI version (e.g., `~/Downloads/RHOAI3.5/`).

2. **Extract text** from each relevant PDF:

```bash
mkdir -p /tmp/<slug>-docs
pdftotext ~/Downloads/RHOAI<version>/<topic>.pdf /tmp/<slug>-docs/<topic>.txt
```

3. **Grep for specific topics** to find the authoritative commands, manifests,
   and console navigation paths:

```bash
grep -n 'InferenceService\|ServingRuntime' /tmp/<slug>-docs/*.txt
```

4. **Store extraction references** in the RAC repo for traceability:

```bash
mkdir -p ~/git/zt-<slug>-rac/assets/doc-extracts
cp /tmp/<slug>-docs/*.txt ~/git/zt-<slug>-rac/assets/doc-extracts/
```

Only extract the PDFs relevant to the feature — not the entire doc bundle.

---

## Maturity-Specific Scaffolding

### antora.yml attribute

Always set `feature_maturity` in `content/antora.yml`:

```yaml
asciidoc:
  attributes:
    feature_maturity: "GA"   # or "TP" or "DP"
```

### index.adoc banners

For TP and DP features, add conditional banners after the page title:

```asciidoc
ifeval::["{feature_maturity}" == "TP"]
WARNING: This feature is a *Technology Preview*. Technology Preview features are
not supported with Red Hat production service-level agreements (SLAs) and might
not be functionally complete.
endif::[]

ifeval::["{feature_maturity}" == "DP"]
WARNING: This feature is a *Developer Preview*. Developer Preview features are
provided as-is with no support and no guarantee of future availability.
endif::[]
```

### Content depth by maturity

| Maturity | Exercises | Execute blocks | Verify sections | Notes |
|----------|-----------|----------------|-----------------|-------|
| GA | Full hands-on | `[source,bash,role="execute",subs="attributes"]` | `=== Verify` after each exercise | Default mode |
| TP | Full hands-on | Same as GA | Same as GA | Add NOTE before API-unstable steps |
| DP | Guided tour | Fewer; use `[source,bash]` (no `role="execute"`) for observe-only | Omit or simplify | Descriptive prose, explore steps |

---

## Self-Check Checklist

Before reporting content as ready, verify:

- [ ] All `// TODO(enrichment)` markers are resolved (only `// TODO: capture screenshot` for images may remain)
- [ ] Every execute block containing `{...}` attribute placeholders has `subs="attributes"` (or `subs="attributes,callouts"` if callouts are also used)
- [ ] `=== Verify` sections reference concrete expected output from the product docs, not vague "you should see the result"
- [ ] Content not found in docs is marked `// NOT-IN-DOCS: <reason>`
- [ ] `feature_maturity` is set in `content/antora.yml`
- [ ] TP/DP features have the correct `ifeval` banner in `index.adoc`
- [ ] Conclusion page links the specific docs chapter (not just the top-level doc URL)

---

## Before/After Example

**Before (TODO stub):**

```asciidoc
== Exercise 1: Deploy the model

// TODO(enrichment): add the real model deployment command from the RHOAI docs.

Deploy the model to your project.

[source,bash,role="execute",subs="attributes+"]
----
# TODO(enrichment): real command
oc status
----

=== Verify

The command completes without error.
```

**After (doc-grounded):**

```asciidoc
== Exercise 1: Deploy the model

Deploy a vLLM ServingRuntime and InferenceService for your model.

. Apply the ServingRuntime:
+
[source,yaml]
----
apiVersion: serving.kserve.io/v1alpha1
kind: ServingRuntime
metadata:
  name: vllm-runtime
spec:
  supportedModelFormats:
    - name: vLLM                          # <1>
  containers:
    - name: kserve-container
      image: quay.io/modh/vllm:rhoai-2.20 # <2>
----
<1> *Model format* — selects the vLLM serving runtime.
<2> *Container image* — use the RHOAI-shipped image; do not substitute upstream.

. Apply it:
+
[source,bash,role="execute",subs="attributes"]
----
oc apply -f serving-runtime.yaml -n {guid}-{user}
----

=== Verify

[source,bash,role="execute",subs="attributes"]
----
oc get servingruntimes -n {guid}-{user}
----

You should see `vllm-runtime` with `READY: True`.
```

**Doc evidence:** `grep -n 'ServingRuntime\|vllm' /tmp/llmd-docs/model-serving.txt`
→ lines 142-168 document the vLLM runtime CR schema.
