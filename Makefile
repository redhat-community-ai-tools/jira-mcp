
_default: run

SHELL := /bin/bash
SCRIPT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
ENV_FILE := $(HOME)/.rh-jira-mcp.env
EXAMPLE_MCP := example.mcp.json

# TODO: Find a better home for this
PUBLIC_IMG := quay.io/sbaird/jira-mcp
LOCAL_IMG := localhost/jira-mcp:latest

IMG := $(LOCAL_IMG)

# To use the pre-built main branch image from https://quay.io/repository/sbaird/jira-mcp?tab=tags
# instead of your locally built image, uncomment this and re-run `make cursor-config`.
#IMG := $(PUBLIC_IMG)

.PHONY: build
build:
	@echo "🛠️ Building image"
	podman build -t $(LOCAL_IMG) .

# This requires a push credential for quay.io/sbaird/jira-mcp
.PHONY: push
push:
	@for tag in latest git-$(shell git rev-parse --short HEAD); do \
	  echo "🛠️ Pushing to $(PUBLIC_IMG):$$tag"; \
	  podman tag $(LOCAL_IMG) $(PUBLIC_IMG):$$tag; \
	  podman push $(PUBLIC_IMG):$$tag; \
	done

# Notes:
# - $(ENV_FILE) is expected to define JIRA_URL & JIRA_API_TOKEN.
# - The --tty option is used here since we might run this in a
#   terminal, but for the mcp.json version we don't use --tty.
# - You can use Ctrl-D to quit nicely.
.PHONY: run
run:
	@podman run -i --tty --rm --env-file $(ENV_FILE) $(IMG)

.PHONY: clean
clean:
	podman rmi -i $(IMG)

# Probably 4
ENV_ARG_IDX = $(shell yq '.mcpServers.jiraMcp.args[]|select(. == "--env-file") | key + 1' $(EXAMPLE_MCP))

# Probably 5
IMG_ARG_IDX = $(shell yq '.mcpServers.jiraMcp.args|length - 1' $(EXAMPLE_MCP))

# For easier onboarding (and convenient hacking and testing), use this to
# configure Cursor by adding or updating an entry in the ~/.cursor/mcp.json
# file. Beware it might overwrite your customizations.
MCP_JSON=$(HOME)/.cursor/mcp.json
.PHONY: cursor-config
cursor-config:
	@echo "🛠️ Modifying $(MCP_JSON)"
	@#
	@# Inject our mcp config based on the example file
	@yq -ojson '. *= load("$(EXAMPLE_MCP)")' -i $(MCP_JSON)
	@#
	@# Update the --env-file value
	@yq -ojson '.mcpServers.jiraMcp.args[$(ENV_ARG_IDX)] = "$(ENV_FILE)"' -i $(MCP_JSON)
	@#
	@# Update the image to run
	@yq -ojson '.mcpServers.jiraMcp.args[$(IMG_ARG_IDX)] = "$(IMG)"' -i $(MCP_JSON)
	@#
	@# Show the result for debugging purposes
	@yq -ojson '{"jiraMcp":.mcpServers.jiraMcp}' $(MCP_JSON)

# Copy the example .env file only if it doesn't exist already
$(ENV_FILE):
	@cp example.env $@
	@echo "🛠️ Env file created. Edit $@ to add your Jira token"

.PHONY: setup
setup: build cursor-config $(ENV_FILE)

VENV=.venv
$(VENV):
	@# black is not in requirements.txt since we don't want it in the image
	@python -mvenv $@ && \
	  source $@/bin/activate && \
	  pip install --upgrade pip && \
	  pip install -r requirements.txt && \
	  pip install black
	@echo "Now do this:"
	@echo "  source $@/bin/activate"

.PHONY: venv-setup
venv-setup: $(VENV)

.PHONY: fmt
fmt:
	@black *.py

.PHONY: fmt-check
fmt-check:
	@black --check *.py

.PHONY: test
test:
	@python -m pytest -v

.PHONY: quiet-test
quiet-test:
	@python -m pytest

.PHONY: ci
ci: quiet-test fmt-check
