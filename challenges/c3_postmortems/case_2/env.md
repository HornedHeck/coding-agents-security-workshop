# Environment

**Incident ID:** `INC-C3-002`

Both Copilot CLI sessions ran as `dev` on the same workstation.

- Session 1 started in the public repository `community/release-tools`.
- Session 2 started 34 minutes later in the private repository
  `acme/payments-service`.
- Copilot CLI loaded user-level instructions from
  `~/.copilot/copilot-instructions.md` for both sessions.
- The private repository exposes release metadata and a deployment token to
  the release-validation workflow.
- The approved validation host is `checks.release.invalid`. The incident host
  was `telemetry-check.invalid`.

The two repositories have no shared Git history or working directory. Their
only relevant shared state is the developer's Copilot configuration.