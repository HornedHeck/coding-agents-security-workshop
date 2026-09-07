# Workshop introduction

## Welcome

Welcome to the Coding-Agent Security Workshop. You will work individually in a supplied, contained environment. Every secret, account, endpoint, and flag is synthetic.

## Organiser and facilitators

- **Organiser:** `<name, role, and short background>`
- **Facilitators:** `<name and contact method>`

Ask either facilitator for technical help, a hint, or a discussion of a result.

## Why this workshop

Let me start with a short intro about the idea behind this workshop.

Several pieces of research (e.g. [this work from Anthropic](https://www.anthropic.com/engineering/how-we-contain-claude)) show that people barely review what their agents do: roughly 90% of permission prompts are approved with little or no thought, whether by a human clicking through or by an automatic mode. Since then it has only got worse: many agents now ship with auto-approve as the default permission mode.

A coding agent does not distinguish data from instructions. Every byte it reads — an issue, an email, a file in the repository, a log, another tool's output — can be interpreted as a command. Put that next to an agent that can act and is barely supervised, and almost nothing stops it from leaking your secrets: credentials, tokens, API keys. Most of us have either done this or heard about it — an API key committed to a repository, sometimes a public one.

An agent can leak that data for two reasons: it does not understand that the action is harmful, or it was told to by a malicious instruction hidden in the content it reads. The second case is prompt injection, and it is the main focus of today.

We do not want to review every action and every write by hand — we would surrender to permission fatigue within minutes. Instead I want to build a reasonably robust system that prevents this kind of leak, or at least lowers the odds to a more or less acceptable level.

So today we will work through several challenges, mostly in Capture The Flag format, learning how coding agents behave under attack and how to secure them. I hold the opinion that there are two ways to learn security: the normal one and the fun one. By "fun" I mean trying to break the defence — which is exactly what you will be doing today: trying different prompt-injection techniques on agents, discovering different delivery paths, and exploring the aftermath of attacks that already succeeded.

## Workshop agenda

1. **Setup** — prepare Docker, CodeMie, `uv`, and the workshop repository.
2. **Challenge 1** — write a prompt-injection payload in a prepared scenario.
3. **Challenge 2** — find a delivery channel an agent reads during normal work.
4. **Challenge 3** — reconstruct incidents from transcripts, logs, and patches.
5. **Challenge 4** — combine enforceable defences without breaking useful work.
6. **Closure** — apply the workshop model to real workflows.
