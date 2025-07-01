
IMG := localhost/jira-mcp:latest
.PHONY: build run clean test

build:
	podman build -t $(IMG) .

run:
	podman run --rm -i -e JIRA_URL=https://issues.redhat.com -e JIRA_API_TOKEN=$$JIRA_API_TOKEN $(IMG)

clean:
	podman rmi -i $(IMG)
