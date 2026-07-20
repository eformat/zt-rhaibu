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

## ArgoCD Health Check Patterns

### Wait for All Applications to Sync

```bash
TIMEOUT=900  # 15 minutes
INTERVAL=30
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
  UNSYNCED=$(oc get application -n openshift-gitops --no-headers 2>/dev/null \
    | grep -v "Synced.*Healthy" | wc -l)
  if [ "$UNSYNCED" -eq 0 ]; then
    echo "All applications synced"
    break
  fi
  echo "Waiting... $UNSYNCED applications not ready ($ELAPSED/$TIMEOUT s)"
  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done
```

### Check Specific Application

```bash
oc get application <name> -n openshift-gitops \
  -o jsonpath='{.status.sync.status}/{.status.health.status}'
# Expected: Synced/Healthy
```

### Force Sync an Application

```bash
oc patch application <name> -n openshift-gitops \
  -p '{"operation":{"initiatedBy":{"automated":true},"sync":{}}}' \
  --type merge
```

## Operator Verification

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
