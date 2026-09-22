# Cross-Workshop Navigation Reference

Concrete AsciiDoc patterns for linking workshops in a multi-workshop catalog.
See WORKSHOP-COMMON-RULES.md Section 11 for the governing rules (N.1–N.3).

---

## Antora Cross-Component Xref Syntax

Each workshop is a named Antora component. The component name is set in
`content/antora.yml`:

```yaml
name: my-feature-slug
```

Cross-component xrefs use this name as the target:

```asciidoc
xref:my-feature-slug::index.adoc[My Feature Workshop]
xref:my-feature-slug:ROOT:module-01-hands-on.adoc[Module 1: Hands-on]
```

The `::` separator means "default version of the named component." The
`:ROOT:` variant targets a specific module (almost always ROOT for showroom
workshops).

Cross-component xrefs only resolve when both workshops are registered as
content sources in the same Antora playbook (`antora-playbook.yml` or
`site.yml`).

---

## Conclusion Template — "Where next in the catalog"

Add this section to `conclusion.adoc` after the `== Resources` section:

```asciidoc
== Where next in the catalog

Continue your learning journey with these related workshops:

* xref:sibling-one::index.adoc[Sibling One Workshop Title]
* xref:sibling-two::index.adoc[Sibling Two Workshop Title]
* xref:sibling-three::index.adoc[Sibling Three Workshop Title]
```

**Guidelines:**

- List 1–3 related workshops, ordered by relevance
- Use workshops that build on the skills learned in this one
- Avoid listing the entire catalog — pick the most natural next steps

---

## Index Prerequisites Template

Add prerequisite xrefs to the `== Prerequisites` section in `index.adoc`:

```asciidoc
== Prerequisites

* An OpenShift cluster with RHOAI {rhoai_version} installed
* Basic familiarity with the `oc` CLI
* Recommended prerequisite: complete the xref:prereq-slug::index.adoc[Prerequisite Workshop Title] workshop first
```

**Guidelines:**

- Only add prerequisites that are genuinely required — not every related workshop
- Use "Recommended prerequisite" phrasing (not "Required") to keep each workshop approachable
- The xref lets learners jump directly to the prerequisite

---

## Standalone Coherence — Bridge Paragraph

When a workshop references content from a sibling but must remain
standalone-buildable, add a bridge paragraph:

```asciidoc
TIP: If you have not completed the
xref:prereq-slug::index.adoc[Prerequisite Workshop], the summary below covers
what you need to continue.

The prerequisite workshop deploys a vLLM serving runtime and
InferenceService. For this workshop you need a running inference endpoint — if
you already have one, skip to Exercise 2.
```

This pattern lets the workshop work both for learners following the full catalog
path and for those who arrive directly.

---

## p-zero-lessons Context

When publishing to `p-zero-lessons`, each workshop lives at `lessons/<slug>/`:

```
p-zero-lessons/
  antora-playbook.yml   ← register each lesson as a content source
  lessons/
    my-feature/
      content/
        antora.yml      ← name: my-feature
        modules/ROOT/...
    sibling-feature/
      content/
        antora.yml      ← name: sibling-feature
        modules/ROOT/...
```

The component name in `antora.yml` (`name: my-feature`) is the xref target.
Cross-component xrefs resolve because both components are listed in
`antora-playbook.yml`.

For standalone deployments (single workshop on its own cluster), cross-component
xrefs will render as broken links. Treat them as optional enhancements — the
workshop content must still make sense without them.
