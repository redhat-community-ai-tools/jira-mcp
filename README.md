# redhat-ai-tools/jira-mcp

A containerized MCP server for Cursor to provide access to Jira.

> [!IMPORTANT]
> This project is experimental and was initially created as a learning exercise.
> Be aware there are more capable and mature Jira MCP solutions available,
> such as [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian),
> and Atlassian's own [MCP Server](https://www.atlassian.com/platform/remote-mcp-server).

## Cursor config

Example configuration file for Cursor, probably in `~/.cursor/mcp.json`:

## Prerequisites

- **Podman** - Install with `sudo dnf install podman` (Fedora/RHEL) or `brew install podman` (macOS)
- **Make** - Usually pre-installed on most systems


## Quick Start

1. **Build the Podman Image:**
   ```bash
   make build
   ```
2. **Get Your Jira API Token:**
   Go to [Red Hat Jira Personal Access Tokens](https://issues.redhat.com/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens) and create a new token.
3. **Configure Cursor:**
   Add this to your `~/.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "jira-mcp": {
         "command": "podman",
         "args": ["run", "--rm", "-i", "-e", "JIRA_URL=https://issues.redhat.com", "-e", "JIRA_API_TOKEN=${JIRA_API_TOKEN}", "jira-mcp:latest"],
         "description": "A containerized MCP server to query Jira issues"
       }
     }
   }
   ```

> **Note:** You do not need to manually run the container. Cursor will automatically start the MCP server when needed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
