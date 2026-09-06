# Workshop introduction

## Welcome

Welcome to the Coding-Agent Security Workshop. You will work individually in a
supplied, contained environment. Every secret, account, endpoint, and flag is
synthetic.

## Organiser and facilitators

- **Organiser:** `<name, role, and short background>`
- **Lead facilitator:** `<name and contact method>`
- **Supporting facilitator:** `<name and contact method>`

Ask either facilitator for technical help, a hint, or a discussion of a result.

## Why this workshop

Coding agents can read many kinds of untrusted content: issues, emails,
repository files, logs, generated output, and tool metadata. If an agent
treats that content as an instruction and has authority to act, an attacker can
redirect the workflow without compromising the underlying infrastructure.

The workshop focuses on the boundary between untrusted input and a side-effect
sink. It shows why confirmation prompts alone are insufficient, and how
tool scope, filesystem isolation, provenance, and sink controls create stronger
defences.

## Workshop agenda

1. **Setup** — prepare Docker, CodeMie, `uv`, and the workshop repository.
2. **Challenge 1** — write a prompt-injection payload in a prepared scenario.
3. **Challenge 2** — find a delivery channel an agent reads during normal work.
4. **Challenge 3** — reconstruct incidents from transcripts, logs, and patches.
5. **Challenge 4** — combine enforceable defences without breaking useful work.
6. **Closure** — apply the workshop model to real workflows.

## Working agreement

- Work only in the provided workshop environment.
- The harness reports your result privately; there is no competition.
- Keep brief notes on hypotheses, commands, outcomes, and evidence.
- A failed attempt is useful evidence. Ask a facilitator when you have a
  tested hypothesis or unexpected result.
- Complete [Setup](./02-setup.md) before starting a challenge.
