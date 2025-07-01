
_default: run

SHELL := /bin/bash
IMG := localhost/jira-mcp:latest
.PHONY: build run clean test

build:
	podman build -t $(IMG) .

run:
	source .env && export JIRA_URL JIRA_API_TOKEN && podman run --rm -i -e JIRA_URL -e JIRA_API_TOKEN $(IMG)

clean:
	podman rmi -i $(IMG)
