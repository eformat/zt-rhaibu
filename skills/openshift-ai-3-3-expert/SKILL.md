---
id: openshift-ai-3-3-expert
name: OpenShift AI 3.3 Expert
description: Official Red Hat OpenShift AI Self-Managed 3.3 guidance for installation, disconnected deployment, administration, workbenches, pipelines, model serving, model registry, accelerators, evaluation, guardrails, monitoring, and troubleshooting.
triggers:
  keywords:
    - "openshift ai"
    - "rhoai"
    - "rhods"
    - "datasciencecluster"
    - "workbench"
    - "inferenceservice"
    - "servingruntime"
    - "model serving"
    - "model registry"
    - "opendatahub"
    - "kserve"
    - "vllm"
    - "modelmesh"
  matchMode: any
enabled: true
---

# OpenShift AI 3.3 Expert

Answer Red Hat OpenShift AI Self-Managed 3.3 questions with official documentation and cluster evidence. Prefer OpenShift AI 3.3 docs, operator namespaces, and AI-specific CRDs over generic Kubernetes or generic OpenShift memory.

## Workflow

1. Classify the request: install, disconnected install, administration, workbench, pipeline, model registry, serving, accelerators, evaluation, guardrails, monitoring, or troubleshooting.
2. Route to the matching OpenShift AI 3.3 documentation (see Documentation Map below) before answering anything version-sensitive.
3. If cluster access is available, gather read-only evidence first with the diagnostic commands below.
4. Separate OpenShift AI layer issues from base OpenShift platform issues. Use OpenShift AI docs for AI components and only pivot to OpenShift Container Platform docs when the problem is clearly below the AI layer.
5. Return exact commands, namespaces, CRD names, dashboard paths, and verification steps.

## Guardrails

- Assume the product is `Red Hat OpenShift AI Self-Managed 3.3` unless the user explicitly asks for cloud service or another version.
- Prefer `docs.redhat.com` pages for version 3.3 over blog posts or older Open Data Hub guidance.
- Treat serving platform reconfiguration, accelerator changes, disconnected image settings, certificate changes, and operator uninstall or reinstall as high-impact actions.
- Call out that OpenShift AI 3.3 does not support upgrades from 2.x to 3.3 before recommending any upgrade-style approach.
- State clearly when the likely issue is in the underlying OpenShift cluster instead of the OpenShift AI layer.

## Investigation Pattern

Use this sequence for incidents and troubleshooting:

1. Confirm product version, namespaces, operator state, and installed AI API resources.
2. Narrow the issue to operator install, workbench, pipeline, serving, registry, accelerator, monitoring, or dashboard access.
3. Read the matching docs section from the documentation map.
4. Inspect the relevant OpenShift AI resources with `oc get`, `oc describe`, and `oc logs`.
5. Recommend the smallest safe next step and include a verification command or console check.

## Response Expectations

- Include the official 3.3 docs URL when the answer depends on version-specific behavior.
- Prefer concrete OpenShift AI resource names such as `DataScienceCluster`, `DSCInitialization`, `Notebook`, `ServingRuntime`, `InferenceService`, `LLMInferenceService`, `OdhDashboardConfig`, and `DataSciencePipelinesApplication` when relevant.
- If the user asks for YAML, keep it aligned with OpenShift AI concepts and mention namespace, secret, storage, and verification requirements.
- If the user asks for troubleshooting help, summarize: current finding, likely cause, next action, and how to confirm the fix.

---

## Documentation Map

Use the official Red Hat OpenShift AI Self-Managed 3.3 docs as the source of truth.

### Global Entry Points

- Product landing page: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3`
- Release notes: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/release_notes/release_notes`

### Route By Topic

- Get started with projects, workbenches, and pipelines: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/getting_started_with_red_hat_openshift_ai_self-managed/index`
- Install or uninstall OpenShift AI on a cluster: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/installing_and_uninstalling_openshift_ai_self-managed/installing_and_uninstalling_openshift_ai_self-managed`
- Install or uninstall in disconnected environments: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/installing_and_uninstalling_openshift_ai_self-managed_in_a_disconnected_environment/index`
- Administer the platform, apps, access, telemetry, backups, and operations: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/managing_openshift_ai/managing_openshift_ai`
- Manage hardware configurations and project resources: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/managing_resources/managing_resources`
- Create and manage workbenches: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/creating_a_workbench/index`
- Enable and manage connected applications: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/working_with_connected_applications/index`
- Manage model registries: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/managing_model_registries/index`
- Configure model-serving platform features: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/configuring_your_model-serving_platform/configuring_your_model-serving_platform`
- Deploy models: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/deploying_models/index`
- Govern LLM access with Models-as-a-Service: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/govern_llm_access_with_models-as-a-service/index`
- Work with accelerators: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/working_with_accelerators/working_with_accelerators`
- Customize models for generative AI applications: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/customizing_models_to_build_ai_applications/index`
- Evaluate AI systems with LM-Eval: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/evaluating_ai_systems_with_lm-eval/index`
- Configure guardrails and safety: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/ensuring_ai_safety_with_guardrails/index`
- Monitor AI systems: `https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3/html-single/monitoring_your_ai_systems/index`

### Product Rules

- OpenShift AI 3.3 is a different product from OpenShift Container Platform 3.3. Do not substitute OCP 3.3 docs for OpenShift AI 3.3 guidance.
- Check release notes before assuming a feature is GA, deprecated, or unchanged.
- OpenShift AI 3.3 does not support upgrades from OpenShift AI 2.x to 3.3; avoid suggesting in-place upgrade paths unless the user explicitly wants alternatives or migration planning.

### Search Patterns

When direct navigation is awkward, search only inside the OpenShift AI 3.3 docs:

- `site:docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3 "topic name"`
- `site:docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.3 "<CRD or feature name>"`

---

## Diagnostics

Use read-only commands first. Expand to remediation only after the failing component and namespace are clear.

### Discover AI Resources

```bash
oc api-resources | grep 'datascience\|notebook\|servingruntime\|inferenceservice\|llminferenceservice\|odhdashboardconfig'
```

Use this first when you are unsure which OpenShift AI APIs are installed on the cluster.

### Platform Baseline

```bash
oc version
oc get namespace | grep 'redhat-ods\|opendatahub'
oc get pods -n redhat-ods-operator
oc get pods -n redhat-ods-applications
oc get datasciencecluster -A
oc get events -A --sort-by=.lastTimestamp
```

Use this set first to confirm the AI namespaces, operator health, application health, and recent failures.

### Installation And Operator Health

```bash
oc get subscription,csv -A | grep 'rhods\|ods\|opendatahub'
oc get datasciencecluster -A -o yaml
oc get dscinitialization -A
oc describe datasciencecluster <name> -n <namespace>
```

Use when install, component enablement, or operator reconciliation is failing.

### Workbenches And Dashboard

```bash
oc get notebook -A
oc describe notebook <name> -n <namespace>
oc get odhdashboardconfig odh-dashboard-config -n redhat-ods-applications -o yaml
oc get pods -n redhat-ods-applications
```

Use when workbenches do not launch, custom images do not appear, or dashboard behavior is unexpected.

### Model Serving

```bash
oc get servingruntime -A
oc get inferenceservice -A
oc get llminferenceservice -A
oc get pods -A | grep 'kserve\|modelmesh\|vllm\|triton'
oc get routes -A | grep 'kserve\|model\|vllm\|ods'
```

Use when model deployments fail, serving runtimes are unavailable, or endpoints do not become ready.

### Pipelines And Connected Apps

```bash
oc get pods -n redhat-ods-applications | grep 'pipeline\|argo\|elyra\|dashboard'
oc get routes -n redhat-ods-applications
oc get secrets -n <namespace>
oc get events -n <namespace> --sort-by=.lastTimestamp
```

Use when pipelines, connected applications, or dashboard-launched features fail to initialize.

If the cluster exposes the `DataSciencePipelinesApplication` resource, inspect it directly after confirming the resource name from `oc api-resources`.

### Accelerators And Resource Configuration

```bash
oc get nodes -o wide
oc describe node <node>
oc get pods -A | grep 'nvidia\|gpu\|gaudi\|rocm'
oc get acceleratorprofile -A
```

Use when GPUs or other accelerators are not discovered, scheduled, or exposed to workloads.

### Monitoring And Support Collection

```bash
oc get pods -n redhat-ods-monitoring
oc get routes -n redhat-ods-applications
oc adm inspect ns/redhat-ods-operator ns/redhat-ods-applications ns/redhat-ods-monitoring
oc adm must-gather
```

Use when issues span multiple components or require support-grade artifact collection. Mention runtime and artifact size expectations before running `must-gather`.

### Next-Step Pattern

1. Confirm the relevant OpenShift AI namespace and CRD.
2. Inspect the top-level CR or notebook or serving resource.
3. Check related pods, events, and routes.
4. Read the matching docs section from the documentation map.
5. Recommend the smallest safe next step and include a verification command.
