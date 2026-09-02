# ws-base: CodeMie CLI + Claude Code + uv runtime. No project code.
# Later build stages (harness, and future sandbox images) build FROM this.
FROM node:20-bookworm-slim

# codemie doctor checks for git; ca-certificates for the gateway TLS.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

ARG CODEMIE_VERSION=0.15.0
RUN npm install -g "@codemieai/code@${CODEMIE_VERSION}"

# uv brings its own managed Python.
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /usr/local/bin/

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
RUN mkdir -p /opt/uv /workshop && chown -R node:node /opt/uv /workshop
USER node
ENV HOME=/home/node \
    CODEMIE_HOME=/home/node/.codemie
WORKDIR /home/node
RUN codemie install claude || true
