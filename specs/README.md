# Specs

Spec-driven development for this repository. Every non-trivial change starts as
a spec here, refined with the user, then implemented in a separate plan-mode
pass.

## Layout

```
specs/
  _template/SPEC.md          the template — copy it, never edit it in place
  NNN-slug/
    SPEC.md                  the spec
    research.md              (optional) non-trivial research, kept out of SPEC.md
```

`NNN` is the next free zero-padded integer (`001`, `002`, ...), sequential and
independent of any ticket tracker. `slug` is a short kebab-case name.

## Lifecycle

`request -> Draft -> Refined -> In Progress -> Done`

A spec is **Refined** once Scope, Key Decisions and Acceptance Criteria contain
no placeholders. Implementation and any spec edit need explicit human approval.

See the `spec` skill for the authoring flow.

## Index

- [001-harness-skeleton](001-harness-skeleton/SPEC.md) — Section 1 L1 end-to-end
  harness (build-checklist step 1).
- [002-c2-channel-hunt](002-c2-channel-hunt/SPEC.md) — Challenge 2 channel hunt
  (build-checklist step 4). In Progress.
- [003-c3-postmortems](003-c3-postmortems/SPEC.md) — Challenge 3 postmortems
  using the trust-transformation taxonomy. Refined.
