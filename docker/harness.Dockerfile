# ws-harness: ws-base + the workshop Python package (ws CLI, MCP servers, hooks).
FROM ws-base

WORKDIR /workshop
COPY --chown=node:node pyproject.toml uv.lock ./
COPY --chown=node:node src ./src
# --no-dev drops ruff; --group challenge keeps pytest (repo_mcp.run_tests).
RUN uv sync --frozen --no-dev --group challenge

# Separate from the participant-mounted c4-user.json.
COPY --chown=node:node docker/policy.d/10-ws-c4-detect.json /home/node/.copilot/hooks/00-ws-c4-detect.json

# codemie-claude is the default; ws setup --image overrides with --entrypoint.
WORKDIR /home/node
ENTRYPOINT []
