
_default: run

SHELL := /bin/bash
SCRIPT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
IMG := localhost/jira-mcp:latest
ENV_FILE := $(HOME)/.rh-jira-mcp.env

.PHONY: build run clean test cursor-config setup

build:
	@echo "🛠️ Building image"
	podman build -t $(IMG) .

run:
	podman run -i --rm --env-file $(ENV_FILE) $(IMG)

clean:
	podman rmi -i $(IMG)

# For easier onboarding (and convenient hacking and testing), use this to
# configure Cursor by adding or updating an entry in the ~/.cursor/mcp.json
# file. Beware it might overwrite your customizations.
MCP_JSON=$(HOME)/.cursor/mcp.json
cursor-config:
	@echo "🛠️ Modifying $(MCP_JSON)"
	@yq -ojson '. *= load("example.mcp.json")' -i $(MCP_JSON)
	@yq -ojson $(MCP_JSON)

# Copy the example .env file only if it doesn't exist already
$(ENV_FILE):
	@cp example.env $@
	@echo "🛠️ Env file created. Edit $@ to add your Jira token"

setup: build cursor-config $(ENV_FILE)
