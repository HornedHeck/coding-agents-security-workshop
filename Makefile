# Developer commands (macOS). Participants never run make — they use `uv run ws`.
PLATFORM := $(shell uv run python -c "from ws.config import linux_platform; print(linux_platform())")
CODEMIE_VERSION := $(shell uv run python -c "from ws.config import CODEMIE_VERSION; print(CODEMIE_VERSION)")
COPILOT_VERSION := $(shell uv run python -c "from ws.config import COPILOT_VERSION; print(COPILOT_VERSION)")
UV_IMAGE := $(shell uv run python -c "from ws.config import UV_IMAGE; print(UV_IMAGE)")

.PHONY: setup image base harness test test-integration lint fmt clean run

setup:
	uv sync --all-groups

base:
	docker build --platform $(PLATFORM) -t ws-base -f docker/base.Dockerfile \
		--build-arg CODEMIE_VERSION=$(CODEMIE_VERSION) \
		--build-arg COPILOT_VERSION=$(COPILOT_VERSION) \
		--build-arg UV_IMAGE=$(UV_IMAGE) .

harness: base
	docker build --platform $(PLATFORM) -t ws-harness -f docker/harness.Dockerfile .

image: harness

test:
	uv run pytest

test-integration:
	@echo "This makes real CodeMie gateway calls (~\$$0.04, logged by codemie analytics)."
	uv run pytest -m integration

lint:
	uv run ruff check .
	uv run ruff format --check .

fmt:
	uv run ruff format .

run:
	uv run ws run c1

clean:
	rm -rf challenges/*/runs/* .pytest_cache .ruff_cache
