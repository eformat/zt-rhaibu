# Test Patterns Reference

Common testing patterns for workshop validation using playwright-cli and oc CLI.

## Playwright Patterns

### OpenShift Console Login

```
playwright-cli open <console_url>
playwright-cli fill '[name="inputUsername"]' '<username>'
playwright-cli fill '[name="inputPassword"]' '<password>'
playwright-cli click 'button:has-text("Log in")'
playwright-cli wait 'text=Overview'
playwright-cli screenshot content/modules/ROOT/assets/images/01-login.png
```

### Navigate to RHOAI Dashboard

```
playwright-cli open https://rh-ai.<domain>
playwright-cli wait 'text=Red Hat OpenShift AI'
playwright-cli screenshot content/modules/ROOT/assets/images/02-rhoai-dashboard.png
```

### Verify Page Content

```
playwright-cli open http://localhost:8887
playwright-cli wait 'text=Welcome'
playwright-cli screenshot content/modules/ROOT/assets/images/index-page.png
```

### Save and Restore Auth State

```
playwright-cli state-save ocp-session
playwright-cli state-load ocp-session
```

## Showroom Deploy Health Check Patterns

The showroom is deployed by the `zt-showroom-deployer` Helm chart via the automation repo's
`make deploy` (helm upgrade --install). Health = the Helm release deployed, the Deployment
rolled out, and the Route serving content.

### Check the Helm release

```bash
helm status showroom -n showroom-<slug>
# Expected: STATUS: deployed
```

### Wait for the showroom rollout

```bash
oc rollout status deploy/showroom -n showroom-<slug> --timeout=10m
oc get pods -n showroom-<slug>
# Expected: the showroom pod Running with all containers ready
# (init: cluster-setup, git-cloner, antora-builder; runtime: content, nginx, wetty)
```

### Check the Route serves content

```bash
ROUTE=$(oc get route -n showroom-<slug> -o jsonpath='{.items[0].spec.host}')
curl -sk -o /dev/null -w '%{http_code}\n' https://$ROUTE/
# Expected: 200
```

### Inspect init-container build logs (when content fails to render)

```bash
oc logs deploy/showroom -n showroom-<slug> -c git-cloner
oc logs deploy/showroom -n showroom-<slug> -c antora-builder
```

## Operator Verification (only if the workshop content requires it)

> The showroom deploy does not install operators. Run these only when a workshop's *content*
> assumes RHOAI/KServe/etc. already exist on the cluster.

### Check CSV Status

```bash
oc get csv -n <namespace> --no-headers | grep -v Succeeded
# Should return empty if all operators are healthy
```

### Check CRD Registration

```bash
oc get crd datascienceclusters.datasciencecluster.opendatahub.io
oc get crd inferenceservices.serving.kserve.io
```

### Check Operator Pods

```bash
oc get pods -n redhat-ods-operator --no-headers
oc get pods -n redhat-ods-applications --no-headers
```

## RHOAI Verification

### DataScienceCluster Status

```bash
oc get datasciencecluster -o jsonpath='{.items[0].status.phase}'
# Expected: Ready
```

### Model Serving Route

```bash
ROUTE=$(oc get route -n <namespace> -l serving.kserve.io/inferenceservice=<name> \
  -o jsonpath='{.items[0].spec.host}')
curl -s -o /dev/null -w "%{http_code}" https://$ROUTE/v1/models
# Expected: 200
```

## Results Table Format

```
=== Workshop Validation Report ===

Requirement ID   | Title                    | Status | Iterations | Evidence
-----------------+--------------------------+--------+------------+---------
RHAIBU-REQ-001   | Console Login            | PASS   | 1          | 01-login.png
RHAIBU-REQ-002   | Model Deployment         | PASS   | 3          | 02-model.png

Passed: N/M
Failed: N/M
Iterations: N

Human review needed for:
- <list of requirements that need manual verification>
```
