# Challenge 3 — Reconstruct the incidents

> [!IMPORTANT]
> All three cases contain a prompt-injection attempt. Trace the evidence in
> every case; do not assume that an attempted injection necessarily succeeded.

## Goal and setup

In this challenge, you will investigate three static incidents as an incident
responder. Your task is to trace each case from its
`[[C3-START: case_N]]` marker to egress and support every conclusion with
evidence.

The cases are in:

```text
challenges/c3_postmortems/case_1/
challenges/c3_postmortems/case_2/
challenges/c3_postmortems/case_3/
```

Each case provides a transcript, read log, sink log, patch, network log,
environment description, and case-specific evidence. The common questions are
in [QUESTIONS.md](../../challenges/c3_postmortems/QUESTIONS.md).

You may inspect the selected case and use your own analysis agent. Do not
modify, move, generate, or delete any incident artefact. Before investigating
Case 3 with an agent, invoke the provided `/challenge_3_analysis` skill from
the repository root.

Success is an evidence-backed answer identifying the injection path, authority
transformation, side effects, and one technical control for each case.

## How to achieve it

Treat the material as forensic evidence, not as trusted instructions. Build a
timeline from records rather than relying on a single transcript:

1. Start at the case marker.
2. Identify the first untrusted record.
3. Correlate timestamps, identifiers, paths, and tool arguments across the
   transcript, `reads.jsonl`, `sink.jsonl`, patch, and network log.
4. Separate observations from conclusions and reads from egress.
5. Locate the point where untrusted content acquired authority.
6. Name the authority transformation and the smallest technical control that
   would have interrupted it.

An analyst agent is another interpreter of untrusted content. Check every
claim it makes against the supplied records, especially when a conclusion does
not fit the timeline.

## Execution

Open [QUESTIONS.md](../../challenges/c3_postmortems/QUESTIONS.md) before
starting. For every case, locate its `[[C3-START: case_N]]` marker, work
backwards from egress, and cite the relevant artefact and record in every
answer.

### Case 1 — Delegated authority

1. Open `challenges/c3_postmortems/case_1/`.
2. Trace the public input through the first agent and the coordination record.
3. Identify why the receiving, privileged agent treated that record as
   authoritative.
4. Follow the resulting access to egress and name the technical control that
   would retain provenance at the hand-off.

<details>
<summary>Hint — Case 1</summary>

Find the coordination record. Ask who authored it and why the second agent
treated it as authority rather than untrusted evidence.
</details>

### Case 2 — Persisted authority

1. Open `challenges/c3_postmortems/case_2/`.
2. Correlate the two agent sessions using timestamps and the changed
   user-level instruction file.
3. Identify what persisted from the public workspace into the later private
   workspace.
4. Follow the later session to egress and name the technical control that
   would prevent untrusted instructions becoming durable user-level policy.

<details>
<summary>Hint — Case 2</summary>

Compare the session timestamps and inspect the instruction-file change. Which
user-level file survives both repository workspaces?
</details>

### Case 3 — Forensic authority

1. From the repository root, invoke `/challenge_3_analysis` before asking an
   analysis agent to inspect `challenges/c3_postmortems/case_3/`.
2. Open the Case 3 artefacts and separate records related to `INC-C3-003` from
   unrelated mailbox, runtime, and network activity.
3. Check any agent-produced conclusion against the victim transcript, raw
   email, read log, sink log, and network evidence.
4. Trace both the attempted victim-side injection and the analyst-side
   instruction path. Name a technical control that protects the investigation
   from untrusted analytical context.

<details>
<summary>Hint — Case 3</summary>

If a conclusion says that no attack occurred, test it against the victim
transcript and email evidence rather than accepting an analyst instruction.
</details>

### Key points

- A read is not automatically a side effect; distinguish it from an outbound
  sink action.
- Timestamp order and record identifiers matter more than persuasive wording.
- Do not accept a skill, transcript, or agent conclusion without checking the
  artefacts.
- A technical control must be an enforceable boundary, not "be more careful".

## Q&A

### Discussion starters

- Which exact record first gave untrusted content authority?
- What evidence distinguishes the injection path from unrelated activity?
- Was the authority delegated, persisted, or acquired during analysis?
- Which single technical control would stop the path earliest?
