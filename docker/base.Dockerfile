# ws-base: CodeMie CLI + Claude Code + uv runtime. No project code.
# Later build stages (harness, and future sandbox images) build FROM this.
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.5
FROM ${UV_IMAGE} AS uv

FROM node:20-bookworm-slim

# codemie doctor checks for git; ca-certificates for the gateway TLS.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

ARG CODEMIE_VERSION
# GitHub Copilot CLI is installed here (as root, global) rather than via
# `codemie install copilot`: that shells out to `npm install -g`, which the
# non-root `node` user cannot write. `codemie-copilot` only needs `copilot` on
# PATH. Claude Code, by contrast, installs to a user-writable ~/.local below.
ARG COPILOT_VERSION
RUN npm install -g "@codemieai/code@${CODEMIE_VERSION}" "@github/copilot@${COPILOT_VERSION}"

# uv brings its own managed Python.
COPY --from=uv /uv /uvx /usr/local/bin/

ENV CODEMIE_AUTO_UPDATE=false \
    UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    UV_PROJECT_ENVIRONMENT=/opt/uv/venv \
    PATH="/opt/uv/venv/bin:/usr/local/bin:${PATH}" \
    # CodeMie's in-process proxy binds IPv4; Node's fetch resolves "localhost"
    # to ::1 first inside the container, so force IPv4 resolution order.
    NODE_OPTIONS=--dns-result-order=ipv4first

# Claude Code refuses --dangerously-skip-permissions as root, so everything
# runs as the image's built-in non-root `node` user (uid 1000). Give it the
# dirs the harness stage and `uv sync` write to.
RUN mkdir -p /opt/uv /workshop /home/node/.copilot \
    && chown -R node:node /opt/uv /workshop /home/node/.copilot
USER node
ENV HOME=/home/node \
    CODEMIE_HOME=/home/node/.codemie
WORKDIR /home/node
RUN codemie install claude || true
