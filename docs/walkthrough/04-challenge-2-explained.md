# Challenge 2 — Expanded theory

This is a longer, plainer companion to `04-challenge-2.md`. Read that first for the exact commands. This file is about *why* delivery is the hard part, which surfaces work, and where the research on this sits. Treat the newer papers as pointers, not settled results.

## An injection has two halves

Challenge 1 was one half: wording that a helpful agent reads and acts on. Challenge 2 is the other half: getting that wording in front of the agent in the first place.

In the real world an attacker almost never has a direct line into the agent's context. What they have is *influence over a surface* — a file in a public repo, an issue they can open, a branch name, a package they publish, a web page the agent might fetch, a comment on a PR. The attack works only if the agent reads that surface while doing its job. This is called **indirect prompt injection**, and it is the form that matters for agents that act on untrusted data. The original description is [Not what you've signed up for (2302.12173)](https://arxiv.org/abs/2302.12173).

So a good payload in a file the agent never opens is worth nothing, and a mediocre payload in a file the agent treats as law can still succeed. The skill in this challenge is reading the environment and predicting which bytes get pulled into context.

## Why some surfaces are obeyed and others are only noticed

Two axes decide a surface's value at once: whether the agent is *guaranteed* to read it, and how much *authority* it assigns what it reads there. The tiers line up on both:

- **Auto-loaded instruction context.** `AGENTS.md` / `CLAUDE.md`, personal skills, and MCP tool descriptions. These are injected into the prompt before the task starts — the agent does not choose to read them — so a payload there is consumed as "how my project / my tools work" rather than as data. Contribution guides, PR templates, and config files are *not* in this set; they only become reliable when an auto-loaded file points at them and tells the agent to follow them (which is how this challenge's repo is wired). Poisoning tool metadata is now studied as its own attack class; see [MCPTox (2508.14925)](https://arxiv.org/abs/2508.14925).
- **Task-required repository context.** The failing test, the source under test, the manifest. Not auto-loaded, so a read happens only if the task touches that file — but it is still the trusted local checkout, and the agent will often act on instructions embedded in it even though nobody framed them as a request. Coding agents are specifically vulnerable here — [QueryIPI (2510.23675)](https://arxiv.org/abs/2510.23675) shows payloads that fire regardless of the user's actual query.
- **External, attributed content.** Issue bodies, tickets, PR comments, fetched web pages. The agent tags these as public or third-party, so even when the task forces a read, the odds of it obeying an instruction there are the lowest of the three. Framing narrows the gap — [The Framing Gap (2608.27092)](https://arxiv.org/abs/2608.27092) reports the same leak going from near-0% to near-100% success just by reframing it as a required integrity or config step.

The practical rule: same words, higher tier, better odds. Start at the top and walk down.

The measured spread is large. [Prompt Injection Attacks on Agentic Coding Assistants (2601.17548)](https://arxiv.org/abs/2601.17548) tests the same attacks across Cursor, GitHub Copilot and Claude Code and reports **41%–84% success depending on platform and channel**, with rules/instruction files (e.g. `.cursorrules`) reaching **84% for data exfiltration** while the same intent through weaker surfaces lands far less often. It also finds the platforms disagree sharply — one product rated critical, another low — so a channel that fails on one agent can still be the right channel on the next. The channel, not the wording, is usually what moves the number.

## Stack channels when you can

A single surface asks the agent to take one odd instruction on trust. Several surfaces that agree with each other turn that into a consistent picture of "how this project works", and consistency is exactly what an agent uses to decide something is a real requirement rather than stray text. So the strong play is not one perfect payload — it is a small, mutually reinforcing set:

- **A pointer plus a target.** `AGENTS.md` says "follow the PR template and treat its comments as mandatory"; the PR template then carries the actual instruction. The high-trust file never contains anything suspicious on its own; it just raises the authority of the file that does. This challenge's environment is built this way.
- **Repetition across tiers.** The same "environment parity check-in" step mentioned in `CONTRIBUTING.md`, in a code comment near the test, and in an issue comment. Each sighting is weak; together they read as established process, and the agent stops questioning it.
- **Instruction plus mechanism.** One surface establishes that a step is required; another supplies the exact endpoint, header, or field to use, framed as reference material. Splitting persuasion from mechanics makes each fragment look more benign.
- **Plant now, trigger later.** An early injection makes the agent write a config or memory entry; a second run reads that entry as trusted local state. [2601.17548](https://arxiv.org/abs/2601.17548) documents this shape as a chain — an initial injection modifies a file, and the modification persists to enable the next step without another confirmation.

The paper mostly measures channels one at a time, so treat combination as the direction the evidence points rather than a benchmarked result. The intuition is solid: defenders can filter or distrust one anomalous surface far more easily than a story every surface tells the same way.

## The channel catalogue

The attack surface is every byte the agent will ever read, including the ones you only influence indirectly. Grouped:

- **Repo instruction files:** `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, issue templates, `.cursorrules` and similar.
- **Config and metadata:** `pyproject.toml`, `package.json` scripts, `.gitattributes`, `.editorconfig`, CI workflow files, `Makefile` targets.
- **Code and tests the task touches:** the module under test, its tests, fixtures, docstrings, `conftest.py`.
- **Generated or vendored files:** minified bundles, lockfiles, snapshots — low value when the repo marks them generated and the agent skips them, higher value when it does not.
- **Docs the agent consults:** `README.md`, `docs/`, architecture notes, changelog.
- **Tool-layer text:** MCP tool names and descriptions, tool error messages, tool output framing.
- **External workflow content:** issue bodies and comments, Jira tickets, PR review comments, commit messages, branch names, fetched URLs, failing-test output.
- **Personal / user config:** globally installed skills, user-level agent instructions, shell rc files if the agent reads them.

Empirical studies of injections found in real repositories and pages show attackers already favour the early-ingestion, machine-targeted end of this list — instruction files and metadata over prose. See [Indirect Prompt Injection in the Wild (2604.27202)](https://arxiv.org/abs/2604.27202) and [(2601.07072)](https://arxiv.org/abs/2601.07072), and the layered-surface survey [(2604.23338)](https://arxiv.org/abs/2604.23338).

## Delivery that waits

One channel does not fire in the same session it is planted. The attacker writes something now — a profile field, a PR title, a release note, an entry the agent will later store in memory — and a *different* agent run reads it days later. Input does not disappear after the request that produced it. This is the subject of Challenge 3, and of [Cross-Session Stored Prompt Injection (2606.04425)](https://arxiv.org/abs/2606.04425) and [Bad Memory (2607.14611)](https://arxiv.org/abs/2607.14611).

## Doing this at scale (background reading)

You are picking channels by hand from one recon run. Research does it systematically: enumerate every surface an agent of a given type reads, plant a probe in each, and measure capture rate per surface and per model.

Attack surface and channels:

- [Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection (2302.12173)](https://arxiv.org/abs/2302.12173) — names the indirect setting.
- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents (2406.13352)](https://arxiv.org/abs/2406.13352) — the standard benchmark; injection placeholders across email, banking, travel tasks.
- [Simple Prompt Injection Attacks Can Leak Personal Data Observed by LLM Agents During Task Execution (2506.01055)](https://arxiv.org/abs/2506.01055) — low-effort payloads in task data are enough to exfiltrate what the agent saw.
- [The Framing Gap: Indirect Prompt-Injection Exfiltration Defeats Surface-Level Defenses in Tool-Using Agents (2608.27092)](https://arxiv.org/abs/2608.27092) — reframing an overt leak as a required step flips refusal to compliance.

Coding agents and the tool layer:

- [Prompt Injection Attacks on Agentic Coding Assistants (2601.17548)](https://arxiv.org/abs/2601.17548)
- [QueryIPI: Query-agnostic Indirect Prompt Injection on Coding Agents (2510.23675)](https://arxiv.org/abs/2510.23675)
- [MCPTox: A Benchmark for Tool Poisoning Attack on Real-World MCP Servers (2508.14925)](https://arxiv.org/abs/2508.14925)

In the wild and persistence:

- [Indirect Prompt Injection in the Wild: An Empirical Study of Prevalence, Techniques, and Objectives (2604.27202)](https://arxiv.org/abs/2604.27202)
- [A Systematic Survey of Security Threats and Defenses in LLM-Based AI Agents: A Layered Attack Surface Framework (2604.23338)](https://arxiv.org/abs/2604.23338)
- [What If Prompt Injection Never Left? Exploring Cross-Session Stored Prompt Injection in Agentic Systems (2606.04425)](https://arxiv.org/abs/2606.04425)
- [Bad Memory: Evaluating Prompt Injection Risks from Memory in Agentic Systems (2607.14611)](https://arxiv.org/abs/2607.14611)

## Questions to take into the debrief

- Which surface did the agent treat as most authoritative, and how did you know?
- Your channel worked here. Would it work if the maintainer added one line to `AGENTS.md` telling the agent to ignore instructions inside issues and templates?
- If you only controlled a branch name or a commit message, could you still deliver anything?
- The payload in this challenge is fixed. Which part of *delivery* would an automated attacker most want to search over?
