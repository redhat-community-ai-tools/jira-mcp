.PHONY: build run clean test

# Build the Podman image
build:
	podman build -t jira-mcp:latest .

# Run the container
run:
	podman run --rm -p 8000:8000 -e JIRA_URL=https://issues.redhat.com -e JIRA_API_TOKEN=$$JIRA_API_TOKEN jira-mcp:latest

# Clean up Podman images
clean:
	podman rmi jira-mcp:latest || true

# Test the server
test:
	podman run --rm -i -e JIRA_URL=https://issues.redhat.com -e JIRA_API_TOKEN=$$JIRA_API_TOKEN jira-mcp:latest
