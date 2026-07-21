# Workshop Common Rules

**Version**: 1.0

Shared contracts for all workshop-* skills in the OODA pipeline. Every workshop skill
MUST reference this file and follow these rules.

---

## 0. Security — No Secrets (MANDATORY)

Skills MUST NOT produce, accept, or store sensitive information in any file.

**Prohibited content:**
- Real passwords, API keys, tokens, secrets, or credentials
- Internal hostnames, VPN endpoints, bastion IPs, or non-public URLs
- SSH keys, certificates, kubeconfig contents, or private key material

**Required patterns:**
- Use `{attribute}` placeholders for all environment-specific values (e.g., `{password}`, `{openshift_console_url}`)
- Use `example.com`, `192.0.2.x` (RFC 5737), and dummy UUIDs in examples
- Never commit auth state files (playwright state, `.auth-state.json`, kubeconfig)

**Skill behavior:**
- Never ask users to paste credentials into the conversation
- Never write credentials to generated files
- Never echo back real credentials provided by the user

---

## 1. AsciiDoc Code Blocks (REQUIRED)

### Executable Commands

Use `[source,role="execute"]` for every command the learner should run. This enables
the Showroom UI copy/execute button.

```asciidoc
[source,role="execute"]
----
oc get pods -n my-project
----
```

When attribute substitution is needed:

```asciidoc
[source,bash,role="execute",subs="attributes"]
----
oc login {openshift_api_url} -u {user} -p {password}
----
```

**Do NOT use `[.copypaste]`** — it is the older nookbag pattern and is deprecated.

### Non-executable Blocks

- Config/data blocks: `[source,yaml]`, `[source,json]` — no `role="execute"`
- Expected output: plain `----` listing with no source declaration
- AsciiDoc examples: `[source,asciidoc]`

### List Continuation

The `+` on its own line continues a list item (keeps numbering intact):

```asciidoc
. Run the command:
+
[source,role="execute"]
----
oc get pods
----
```

---

## 2. Image Conventions (REQUIRED)

All images go in `content/modules/ROOT/assets/images/`.

### Required Syntax

```asciidoc
image::filename.png[Alt text,link=self,window=blank,width=700]
```

- `link=self` — click opens full-size image
- `window=blank` — opens in new tab
- `width=700` — constrain display width (500-800px typical)
- Alt text is the first positional parameter — make it meaningful for accessibility

### Filename Conventions

- Use deterministic names so re-captures replace existing files: `01-keycloak-login.png`, `06-workbench-creation-form.png`
- Use 2-digit prefix for ordering within a module
- Descriptive slug after the prefix — no `image1.png`

### Placeholders

If an image doesn't exist yet:

```asciidoc
// TODO: capture screenshot
image::create-workbench-form.png[Workbench creation form,link=self,window=blank,width=700]
```

---

## 3. Attribute Substitution (REQUIRED)

Never hardcode cluster-specific values. Use Antora attributes defined in
`content/antora.yml`:

```yaml
asciidoc:
  attributes:
    openshift_console_url: https://console-openshift-console.{deployer_domain}
    user: user1
    password: openshift
    project_name: demo
```

Use `subs="attributes"` on code blocks that contain `{attribute}` values. Without it,
curly-brace placeholders render literally.

---

## 4. RAC Integration (REQUIRED)

Workshop artifacts live in the RAC repo at `~/git/zt-<slug>-rac/`.

**Read from:**
- `requirements/` — acceptance criteria, learning objectives, module structure
- `decisions/` — architectural decisions (content format, infra approach)
- `designs/` — parameter inventory, module flow

**Write to:**
- `assets/` only — observation documents, screenshot evidence, validation reports

**Never modify:**
- `requirements/`, `decisions/`, `designs/` — if a requirement is wrong, flag it and
  ask the user to update it via workshop-orient

---

## 5. Quality Gate (REQUIRED)

Before declaring content ready, run `showroom:verify-content` if the RHDP skills
marketplace plugin is installed.

```
/showroom:verify-content
```

This launches parallel agents per module, checking against Red Hat quality standards:
- AsciiDoc structure and formatting
- Accessibility compliance
- Red Hat style guide
- Technical accuracy

**Severity handling:**
- **Critical** / **High** — must fix before proceeding
- **Warning** — report but do not block
- **Info** / **Recommendation** — optional improvement

If the plugin is not installed, skip this step and note it in the validation report.

---

## 6. Related Skills Convention (REQUIRED)

Every SKILL.md ends with a `## Related Skills` section listing connected skills:

```markdown
## Related Skills

- `/workshop-orient` — Plan the workshop from observations
- `/workshop-do` — Scaffold content and infrastructure
- `/showroom:verify-content` — Validate content against Red Hat standards
```

---

## 7. Skill Coordination Pattern

Skills in the OODA pipeline follow a sequential handoff:

```
Observe → Orient → Do → Act
                    ↑      ↑
              screenshot  verify-content
```

Each skill reads from the previous phase's output and writes to its own output
location. Skills communicate through:
- RAC artifacts (requirements, decisions, designs)
- Git repos (showroom content, automation infrastructure)
- Structured reports (validation tables, evidence maps)

---

**Maintained by:** zt-rhaibu OODA pipeline
