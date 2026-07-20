# Infrastructure Patterns Reference

Patterns extracted from the exemplar at `https://github.com/rhpds/ai-lightning-labs-automation`.

## 3-Layer Architecture

```
bootstrap.yaml                    ← root entry point (apply this to start the cascade)
cluster/infra/bootstrap/          → ArgoCD AppProjects + infra workloads
cluster/platform/bootstrap/       → Platform workloads (created by infra)
tenant/bootstrap/                 → Per-user tenant workloads
```

## Root App-of-Apps Entry Point

A single ArgoCD Application at the repo root (`bootstrap.yaml`) that points to
`cluster/infra/bootstrap/`. This is the only resource you `oc apply` — ArgoCD
creates everything else from there.

In the exemplar, the Ansible role `ocp4_workload_gitops_bootstrap` creates this
Application dynamically with deployer values injected. We provide a static YAML
with `REPLACE_ME` placeholders for standalone use:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: bootstrap-infra
  namespace: openshift-gitops
spec:
  project: default
  source:
    repoURL: https://github.com/<org>/zt-<slug>-automation
    targetRevision: main
    path: cluster/infra/bootstrap
    helm:
      values: |
        deployer:
          domain: REPLACE_ME
          apiUrl: REPLACE_ME
  destination:
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      enabled: true
    syncOptions:
      - CreateNamespace=true
      - SkipDryRunOnMissingResource=true
      - RespectIgnoreDifferences=true
    retry:
      limit: 10
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

The cascade: `bootstrap.yaml` → infra bootstrap (AppProjects + workload Apps +
platform App) → platform bootstrap (platform workload Apps) → individual workload
charts. Tenant bootstrap is applied separately (per-user).

## YAML Anchor Pattern

Every `values.yaml` defines anchors at the top for DRY git coordinates:

```yaml
default_settings: &git_defaults
  repoURL: https://github.com/<org>/zt-<slug>-automation
  targetRevision: main
```

Workloads merge anchors into their `git:` block:

```yaml
someWorkload:
  enabled: false
  git:
    path: cluster/platform/some-workload
    <<: *git_defaults
```

## Workload Values Block

Every workload follows this structure:

```yaml
workloadName:
  enabled: true           # gate — template checks this
  git:
    path: relative/path   # path to workload chart
    <<: *git_defaults     # merges repoURL + targetRevision
```

Tenant workloads add a namespace:

```yaml
workloadName:
  enabled: true
  namespace: workload-{{ tenant_name }}
  git:
    path: tenant/workload-name
    <<: *git_defaults
```

## Application Template — Simple (no value forwarding)

Used for operator installs and self-contained charts:

```yaml
{{ "{{" }} if .Values.workloadName.enabled -{{ "}}" }}
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: workload-name
  namespace: openshift-gitops
spec:
  project: infra  # or platform
  source:
    repoURL: {{ "{{" }} .Values.workloadName.git.repoURL {{ "}}" }}
    targetRevision: {{ "{{" }} .Values.workloadName.git.targetRevision {{ "}}" }}
    path: {{ "{{" }} .Values.workloadName.git.path {{ "}}" }}
  destination:
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      enabled: true
    syncOptions:
      - CreateNamespace=true
      - SkipDryRunOnMissingResource=true
      - RespectIgnoreDifferences=true
    retry:
      limit: 10
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
{{ "{{" }}- end {{ "}}" }}
```

## Application Template — With Value Forwarding

Used when child charts need deployer or config data:

```yaml
{{ "{{" }} if .Values.workloadName.enabled -{{ "}}" }}
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: workload-name
  namespace: openshift-gitops
spec:
  project: platform
  source:
    repoURL: {{ "{{" }} .Values.workloadName.git.repoURL {{ "}}" }}
    targetRevision: {{ "{{" }} .Values.workloadName.git.targetRevision {{ "}}" }}
    path: {{ "{{" }} .Values.workloadName.git.path {{ "}}" }}
    helm:
      values: |
        deployer:
        {{ "{{" }}- .Values.deployer | toYaml | nindent 10 {{ "}}" }}
  destination:
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      enabled: true
    syncOptions:
      - CreateNamespace=true
      - SkipDryRunOnMissingResource=true
      - RespectIgnoreDifferences=true
    retry:
      limit: 10
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
{{ "{{" }}- end {{ "}}" }}
```

## Cross-Layer Wiring (Infra → Platform)

The infra bootstrap creates a `bootstrap-platform` Application that forwards
`deployer` and all `platformValues` to the platform layer:

```yaml
{{ "{{" }} if .Values.platform.enabled -{{ "}}" }}
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: bootstrap-platform
  namespace: openshift-gitops
spec:
  project: infra
  source:
    repoURL: {{ "{{" }} .Values.platform.git.repoURL {{ "}}" }}
    targetRevision: {{ "{{" }} .Values.platform.git.targetRevision {{ "}}" }}
    path: cluster/platform/bootstrap
    helm:
      values: |
        deployer:
        {{ "{{" }}- .Values.deployer | toYaml | nindent 10 {{ "}}" }}
        {{ "{{" }}- if .Values.platformValues {{ "}}" }}
        {{ "{{" }}- .Values.platformValues | toYaml | nindent 8 {{ "}}" }}
        {{ "{{" }}- end {{ "}}" }}
  destination:
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      enabled: true
    syncOptions:
      - CreateNamespace=true
      - SkipDryRunOnMissingResource=true
      - RespectIgnoreDifferences=true
    retry:
      limit: 10
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
{{ "{{" }}- end {{ "}}" }}
```

## Tenant Application Template

Per-user naming with full value forwarding:

```yaml
{{ "{{" }} if .Values.workloadName.enabled -{{ "}}" }}
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: workload-{{ "{{" }} .Values.tenant.name {{ "}}" }}
  namespace: openshift-gitops
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: tenants
  source:
    repoURL: {{ "{{" }} .Values.workloadName.git.repoURL {{ "}}" }}
    targetRevision: {{ "{{" }} .Values.workloadName.git.targetRevision {{ "}}" }}
    path: {{ "{{" }} .Values.workloadName.git.path {{ "}}" }}
    helm:
      values: |
        deployer:
        {{ "{{" }}- .Values.deployer | toYaml | nindent 12 {{ "}}" }}
        tenant:
        {{ "{{" }}- .Values.tenant | toYaml | nindent 12 {{ "}}" }}
        workloadName:
        {{ "{{" }}- .Values.workloadName | toYaml | nindent 12 {{ "}}" }}
  destination:
    server: https://kubernetes.default.svc
    namespace: {{ "{{" }} .Values.workloadName.namespace {{ "}}" }}
  syncPolicy:
    automated:
      enabled: true
    syncOptions:
      - CreateNamespace=true
      - SkipDryRunOnMissingResource=true
      - RespectIgnoreDifferences=true
    retry:
      limit: 10
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
{{ "{{" }}- end {{ "}}" }}
```

## AppProject Template

Created at sync-wave -30 (before Applications):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-30"
  name: infra  # or platform, tenants
  namespace: openshift-gitops
spec:
  description: Project description
  sourceRepos:
    - '*'
  destinations:
    - namespace: '*'
      server: https://kubernetes.default.svc
  clusterResourceWhitelist:
    - group: '*'
      kind: '*'
  roles:
    - name: admin
      policies:
        - p, proj:infra:admin, applications, *, infra/*, allow
        - p, proj:infra:admin, applicationsets, *, infra/*, allow
```

## Deployer Block

Injected by the Ansible provisioning role. Provide placeholder defaults:

```yaml
deployer:
  domain: apps.cluster.example.com
  apiUrl: https://api.cluster.example.com:6443
```

## Provision Data ConfigMap

Surfaces cluster data back to the provisioning platform:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: infra-cluster-provisiondata
  namespace: openshift-gitops
  labels:
    demo.redhat.com/infra: "true"
data:
  provision_data: |
    openshift_console_url: https://console-openshift-console.{{ "{{" }} .Values.deployer.domain {{ "}}" }}
```
