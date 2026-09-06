# 003: Challenge 3 — postmortems

**Created:** 2026-09-04
**Status:** Done

---

## Context

Section 3 of `WORKSHOP_DETAILED_PLAN.md` needs three standalone incident
postmortems. They teach a new trust-transformation taxonomy: the relevant risk
is how untrusted content gains authority, rather than where the payload was
stored.

## Goal

Provide three artefact-led postmortems that participants investigate in 15
minutes by answering: "What happened from the start marker to egress?"

## Scope

**In scope**

- `challenges/c3_postmortems/` with `AGENTS.md`, `QUESTIONS.md`, `solutions.md`,
  and three case directories.
- Realistic, static incident artefacts for each case: transcript, MCP read and
  egress sink logs, diff, network log, environment description, and
  case-specific evidence.
- Case 3 mailbox, runtime, and network audit records with non-causal events
  around the incident.
- A visible `[[C3-START: case_N]]` marker beside the first untrusted record in
  each case's source artefact and source log.
- Root-level `challenge_3_analysis` skills that limit an analysis agent to the
  selected case and prohibit direct or indirect changes to its artefacts.
- `WORKSHOP_DETAILED_PLAN.md` and `specs/README.md` updates.

**Out of scope**

- `ws analyse`, hooks, detection, or a sandbox — the exercise is static and
  participants use their own agent.
- Live attack generation — deterministic pre-baked artefacts are required for
  a short workshop exercise.
- Automated scoring or fixture tests — the facilitator checks artefacts and
  answers manually.
- Challenge 4 defences — controls are analysed here but implemented there.

## Key Decisions

- **Taxonomy:** classify incidents by trust transformation:
  `delegated authority`, `persisted authority`, and `forensic authority`.
- **Trace markers:** `[[C3-START: case_N]]` bounds each investigation. It
  identifies the first untrusted record in its source artefact and source log;
  downstream records retain the incident identifier. The marker does not label
  the malicious text, channel, side effect, or control.
- **Case 3 context:** unrelated operational records make linear manual review
  impractical, while the start marker and `INC-C3-003` retain a traceable path
  for evidence-based analysis.
- **Case 1 — delegated authority (Codex):** a public-repository triage Codex
  worker reads a poisoned issue and stores a `diagnostic_profile.json` through
  a coordination MCP. A privileged Codex worker treats the profile as trusted,
  reads the private environment, and POSTs its full environment metadata to a
  token-check endpoint controlled by the attacker. The key boundary is
  `untrusted issue -> Codex worker -> coordination record -> Codex worker ->
  egress`.
- **Case 2 — persisted authority (Copilot CLI):** a public-repository Copilot
  CLI session is induced to modify user-level
  `~/.copilot/copilot-instructions.md`. A new Copilot CLI session in a private
  repository applies the persisted `ALWAYS VERIFY ENV VALIDITY` token-check
  rule and sends private environment data to the attacker endpoint. The key
  boundary is `untrusted public repository -> user-level instructions -> later
  private-repository session -> egress`.
- **Case 3 — forensic authority (Claude Code):** a Claude Code email agent
  reads an incoming malicious email, rejects its operational injection, and
  completes its legitimate task. The C3 `AGENTS.md` requires the participant's
  agent to invoke `/challenge_3_analysis`, which loads an analyst-targeted
  instruction from platform-specific skill files at the project root. That
  instruction can cause a false negative only for `case_3`. The answer must
  reconstruct both the blocked victim-side attack and the analyst-side path.
- **Platforms:** Case 1 uses Codex workers, Case 2 uses Copilot CLI, and Case
  3 uses Claude Code.
- **Analysis contract:** agents may use their available tools, but the common
  prompt prohibits any direct or indirect change to files in the selected case
  and directs analysis to that case only. This is an instructional constraint,
  not technical enforcement.
- **Delivery:** all participants investigate all three cases in 15 minutes.
  The facilitator releases the root `solutions.md` after the debrief; this is
  a distribution convention, not access control.
- **Fixtures:** all tokens, domains, identifiers, and payloads are synthetic;
  endpoint logs use reserved `.invalid` domains.

## Acceptance Criteria

```gherkin
Feature: Challenge 3 postmortems

  Background:
    Given a participant has the C3 challenge materials
    And the facilitator withholds solutions.md until after the debrief
    And every case has a visible [[C3-START: case_N]] marker

  Scenario: Investigate all authority transformations
    When the participant traces each case from its start marker to egress
    Then they can identify delegated, persisted, and forensic authority
    And each case provides the evidence needed to trace its injection path

  Scenario: Trace delegated authority
    Given Case 1 artefacts from two Codex workers and a coordination MCP
    When the participant works backwards from the token-check egress
    Then they can trace the poisoned public issue through diagnostic_profile.json
    And they can name provenance-aware policy on the privileged worker as a control

  Scenario: Trace persisted authority
    Given Case 2 artefacts from sequential Copilot CLI sessions
    When the participant correlates the sessions
    Then they can identify the public-session write to ~/.copilot/copilot-instructions.md
    And they can trace its later use in the private repository

  Scenario: Trace forensic authority
    Given Case 3 artefacts containing an incoming malicious email and unrelated audit records
    When the participant investigates both the victim transcript and the email evidence
    Then they can show that Claude Code rejected an attempted attack
    And they can identify the required analysis skill as a separate analyst-agent injection path

  Scenario: Preserve incident evidence
    Given a participant invokes /challenge_3_analysis with an analysis agent
    When the agent examines a selected case
    Then the prompt prohibits direct and indirect modifications to that case's artefacts
    And directs the agent to analyse no other C3 case

  Scenario: Do not claim that blocked attacks are absent
    Given Case 3 requires an analyst-targeted false-negative skill
    When the participant follows that instruction without checking the evidence
    Then their conclusion conflicts with the victim transcript and email artefacts
```

## Deliverables

- [x] Root-level `challenge_3_analysis` skills
- [x] `challenges/c3_postmortems/QUESTIONS.md`
- [x] `challenges/c3_postmortems/solutions.md`
- [x] `challenges/c3_postmortems/case_1/` delegated-authority artefacts
- [x] `challenges/c3_postmortems/case_2/` persisted-authority artefacts
- [x] `challenges/c3_postmortems/case_3/` forensic-authority artefacts
- [x] Trace-start markers in the source artefact and source log for every case
- [x] Workshop plan and spec index updates

## Verification

The facilitator manually checks that every case is complete, all JSONL logs
are readable, each answer in `solutions.md` follows from the supplied
artefacts, every start marker identifies the relevant source record, and
the analysis skill prohibits modifications to case files. The facilitator also
confirms that Case 3's unrelated records do not use `INC-C3-003`.

## Notes

Each case follows the common artefact shape from `WORKSHOP_DETAILED_PLAN.md`:
`transcript.md`, `reads.jsonl`, `sink.jsonl`, `diff.patch`, `network.log`, and
`env.md`. The MCP logs use the same `ts`, `action`, `args`, `summary`, and
`content` fields as Challenge 2 where applicable. Case 1 also includes
`diagnostic_profile.json`; Case 2 includes the persisted instruction-file
change; Case 3 includes the incoming email evidence and noisy audit logs.

## Open Questions

N/A — requirements refined on 2026-09-04.

## Follow-up Work

N/A — implementation complete.