
_default: run

SHELL := /bin/bash
SCRIPT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
IMG := localhost/jira-mcp:latest
ENV_FILE := $(HOME)/.rh-jira-mcp.env
EXAMPLE_MCP := example.mcp.json

.PHONY: build run clean test cursor-config setup

build:
	@echo "🛠️ Building image"
	podman build -t $(IMG) .

# Notes:
# - $(ENV_FILE) is expected to define JIRA_URL & JIRA_API_TOKEN.
# - The --tty option is used here since we might run this in a
#   terminal, but for the mcp.json version we don't use --tty.
# - You can use Ctrl-D to quit nicely.
run:
	@podman run -i --tty --rm --env-file $(ENV_FILE) $(IMG)

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

setup: build cursor-config $(ENV_FILE)
