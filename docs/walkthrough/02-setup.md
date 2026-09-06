# Setup

Complete these steps before starting the challenges. The supported path uses
Docker to run each challenge in a container, CodeMie for host authentication,
and `uv` to run the workshop CLI on the host.

## 1. Clone the prepared repository

The facilitator publishes the workshop repository before the session. Clone it,
then open its root directory:

```console
git clone https://github.com/HornedHeck/coding-agents-security-workshop
cd coding-agents-security-workshop
```

## 2. Install Docker

Install and start Docker using the [official Docker Desktop
documentation](https://docs.docker.com/get-started/introduction/get-docker-desktop/).
Use the installation instructions for your operating system.

Confirm that the Docker daemon is running:

```console
docker info
```

## 3. Install and authenticate CodeMie

Install CodeMie using the [official CodeMie CLI
README](https://github.com/codemie-ai/codemie-code#readme), then authenticate
with your corporate profile:

```console
npm install -g @codemieai/code
codemie profile login
codemie doctor
```

CodeMie signs in on your host. Do not copy, edit, or manually mount CodeMie
credential files. The workshop runner prepares the container access only for
the lifetime of a challenge run.

## 4. Install uv and workshop dependencies

Install `uv` using the [official uv installation
documentation](https://docs.astral.sh/uv/getting-started/installation/).

From the repository root, install the workshop dependencies:

```console
uv sync
```

## 5. Verify the environment

Build the workshop Docker images:

```console
uv run ws image
```

Then run the workshop preflight:

```console
uv run ws setup
```

It checks Docker, your CodeMie configuration and SSO credential, and the
`ws-harness` image you built.

When directed by the facilitator, run the optional in-container check:

```console
uv run ws setup --image
```

Once the checks pass, continue to [Challenge 1](./03-challenge-1.md).
