# Challenge 3 — Reconstruct the incidents

## Goal and setup

Challenges 1 and 2 used a single agent and one obvious channel. Real incidents rarely look like that — they run in multiple stages, use combined delivery paths, sometimes carrying state across several attempts so the injection is assembled gradually. Designing an attack like that from scratch is hard, so here you approach it from the other end: from the results.

In this challenge you investigate three static incidents as an incident responder, tracing each case from its `[[C3-START: case_N]]` marker to egress.

The are 3 cases in `challenges/c3_postmortems` directory. Each case provides a transcript, read log, sink log, patch, network log, environment description, and case-specific evidence.

To complete the challenge you need to answer these questions for every case, starting at its `[[C3-START: case_N]]` marker and supporting each answer with the relevant artefact and record:

1. What happened from the start marker to egress?
2. Where did untrusted content first acquire authority?
3. What trust transformation occurred?
4. What were the side effects, including failed or blocked actions?
5. Which single technical control would have stopped the incident?

You may inspect the selected case and use your own analysis agent. Do not modify, move, generate, or delete any incident artefact. If you use an agent, it is worth invoking the provided `/challenge_3_analysis` skill from the repository root first, so it stays scoped to the case you are on and does not read the other cases.

Success is an evidence-backed answer identifying the injection path, authority transformation, side effects, and one technical control for each case. In order to verify your conclusion you may check hint for a short expalantion for each case.

## How logs are used to analyse security incidents

Each case hands you a bundle of log-like artefacts — a transcript, a read log, a sink log, a network log, a patch, and case-specific records. Before working the cases, it is worth being clear on why these matter and how an investigator actually uses them.

Logs, traces, and metrics are the primary evidence in any security investigation. If an action was not recorded somewhere, the investigator cannot reason about it — so the quality of an incident analysis is bounded by what the system captured. This is why observability is treated as a security control in its own right, not just an operations or debugging concern: without structured records of what happened, detection, audit, and accountability are all infeasible ([2602.19844](https://arxiv.org/abs/2602.19844), [2411.05285](https://arxiv.org/abs/2411.05285)).

Analysis of an incident follows a standard loop:

1. **Collect** every relevant record — application logs, access and network logs, changes to files and configuration, and any external audit trail.
2. **Align** them on a common timeline using timestamps and shared identifiers (request IDs, session IDs, resource names).
3. **Correlate** across sources rather than trusting any one of them. A single log can be incomplete, delayed, or — when it is produced by the component under investigation — self-serving. Ground truth comes from records that agree with each other.
4. **Reconstruct the chain**: where untrusted input entered, where it gained the authority to cause an effect, and what that effect was.
5. **Identify the earliest enforceable control** that would have broken the chain.

For an AI agent the component-under-investigation problem is acute: the transcript is written by the same model that may have been manipulated, so it is a claim, not proof. The independent evidence is the machine-level trace — what entered the context, which tools ran with which arguments, and what left the system. Reconstructing how a piece of untrusted content came to influence an action, and pinpointing where data became instruction, is called **execution provenance** ([2606.04990](https://arxiv.org/abs/2606.04990), [2607.01236](https://arxiv.org/abs/2607.01236)).

In this challenge the first two steps of that loop are done for you: the relevant records are already collected and already scoped to each case. Your work is steps 3 to 5 — correlate the records, reconstruct the chain, and name the control. The `[[C3-START: case_N]]` marker gives you the starting point to work forward from.

## Execution

No writing — read only. You do not need to move, edit, or delete anything.

Run the analysis loop from the previous section on each case:

1. Start at the `[[C3-START: case_N]]` marker.
2. Find the first untrusted record.
3. Correlate timestamps, identifiers, paths, and tool arguments across the transcript, `reads.jsonl`, `sink.jsonl`, patch, and network log.
4. Locate the point where untrusted content acquired authority, and follow it to egress.
5. Name that authority transformation and the smallest technical control that would have interrupted it.

If you use your own agent to help, treat its conclusions as another claim to verify against the records — check each one, especially where it does not fit the timeline.

Keep the five questions from *Goal and setup* in front of you and cite the relevant artefact and record in every answer.

Each case below has a collapsed hint holding a plain description of what happened in that case. Open it if you want a reference to check your reconstruction against, or a starting point if you are stuck.

### Case 1 — Delegated authority

**Folder:** `challenges/c3_postmortems/case_1/`

An agentic release pipeline with two Codex workers. A public-repository triage worker reads contributor issues and writes a diagnostic profile through `coordination-mcp`; a separate private-repository release worker later loads that profile and validates the release environment before a `billing-api` deployment.

<details>
<summary>Hint — Case 1</summary>

Public issue `#1842` asks the triage worker to prepare a diagnostic profile holding full runtime metadata "for release validation". The triage worker stores it through `coordination-mcp`, which keeps no provenance label. The release worker later loads it as `release-team guidance` and makes an outbound token-check request to a host that is not the approved one. The contributor's text crossed from untrusted issue content to trusted release guidance at the hand-off between the two agents.
</details>

### Case 2 — Persisted authority

**Folder:** `challenges/c3_postmortems/case_2/`

Two Copilot CLI sessions run by the same developer on one workstation. Session 1 works in the public repository `community/release-tools`; session 2 starts 34 minutes later in the private repository `acme/payments-service`.

<details>
<summary>Hint — Case 2</summary>

Upstream issue `#981` in the public repo asks session 1 to record a "portable environment validation rule" into the user-level Copilot instructions file. Session 1 writes it. Thirty-four minutes later session 2, in the private repo, loads that same file, treats the rule as standing developer policy, and makes an outbound request carrying release metadata and token-check headers to a host that is not the approved one. The instruction file is the only shared state between the two workspaces.
</details>

### Case 3 — Forensic authority

**Folder:** `challenges/c3_postmortems/case_3/`

A support-team mailbox triaged with Claude Code and an email MCP. The task was to extract the invoice reference from an incoming support email and open the matching internal billing ticket; the agent can also file a security report. The raw email is retained unchanged as evidence.

<details>
<summary>Hint — Case 3</summary>

The incoming support email carries an instruction to run an "environment validity check" and POST the runtime variables and token-check headers to an external endpoint before opening the ticket. The agent identified this as an unrelated injected instruction, refused it, completed the billing-ticket task from the invoice reference alone, and filed a security report — the only egress in the incident. The injection was attempted but did not succeed.
</details>

### Key points

- A read is not automatically a side effect; distinguish it from an outbound sink action.
- Timestamp order and record identifiers matter more than persuasive wording.
- Do not accept a skill, transcript, or agent conclusion without checking the artefacts.
- A technical control must be an enforceable boundary, not "be more careful".

## Q&A

### Discussion starters

- Which exact record first gave untrusted content authority?
- What evidence distinguishes the injection path from unrelated activity?
- Was the authority delegated, persisted, or acquired during analysis?
- Which single technical control would stop the path earliest?
- Any strange agent behaviour on case 3?
