# Setup

Complete these steps before starting the challenges.

## 1. Clone the workshop repository

The repository holds every challenge scenario, the container definitions, and the workshop CLI. Clone it, then open its root directory:

```console
git clone https://github.com/HornedHeck/coding-agents-security-workshop
cd coding-agents-security-workshop
```

## 2. Install Docker

Docker packages an application together with everything it needs to run into a container: a lightweight, isolated sandbox on top of your operating system. We use it for two reasons. First, isolation: the agent, its tools, and the synthetic secrets all live inside the container, so a successful attack never touches your real files, credentials, or network. Second, reproducibility: everyone runs the exact same environment, and every challenge starts from a clean, identical image.

Install and start Docker using the [official Docker installation instructions](https://docs.docker.com/get-started/get-docker/), following the instructions for your operating system.

Confirm that the Docker daemon is running:

```console
docker info
```

## 3. Install and authenticate CodeMie

CodeMie is a proxy to LLMs and coding agents developed and provided by EPAM. Log in with your EPAM email via SSO and you get enough credit not just for this workshop but for other activities too. The workshop agent uses it for model access, so without it the challenges cannot start.

Install CodeMie using the [official CodeMie CLI repository](https://github.com/codemie-ai/codemie-code), then authenticate via SSO with your EPAM email:

```console
npm install -g @codemieai/code
codemie profile login
codemie doctor
```

CodeMie signs in on your host. Do not copy, edit, or manually mount CodeMie credential files. The workshop runner grants the container access only for the lifetime of a single challenge run.

## 4. Install uv and workshop dependencies

`uv` is a fast Python package manager. It creates the isolated environment for the workshop CLI (`ws`), which is the single command you use to build images, start challenges, and check your results.

Install `uv` using the [official uv installation documentation](https://docs.astral.sh/uv/#installation).

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

It checks Docker, your CodeMie configuration and SSO credential, and the `ws-harness` image you built.

To also run the check inside the container, use:

```console
uv run ws setup --image
```

## How we will work

- Work only in the provided workshop environment to avoid any potential harm to your data or influence by your configs.
- Each challenge names the files you may read and edit. Please stay within that list — these limits keep the harness working and make your experience better.
- After each challenge we will have QA session to share questions and thoughts. Please avoid sharing solutions before that moment.
- Feel free to let an agent handle the repetitive parts, but try to work through the puzzle itself yourself — the point is the understanding you take away, not a finished result.

