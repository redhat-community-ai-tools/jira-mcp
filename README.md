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

## Available Tools

This MCP server provides the following tools:

### Issue Search
- `get_jira` - Get details for a specific Jira issue by key.
- `search_issues` - Search issues using JQL

### Project Management
- `list_projects` - List all projects
- `get_project` - Get project details by key
- `get_project_components` - Get components for a project
- `get_project_versions` - Get versions for a project
- `get_project_roles` - Get roles for a project
- `get_project_permission_scheme` - Get permission scheme for a project
- `get_project_issue_types` - Get issue types for a project

### Board & Sprint Management
- `list_boards` - List all boards
- `get_board` - Get board details by ID
- `list_sprints` - List sprints for a board
- `get_sprint` - Get sprint details by ID
- `get_issues_for_board` - Get issues for a board
- `get_issues_for_sprint` - Get issues for a sprint

### User Management
- `search_users` - Search users by query
- `get_user` - Get user details by account ID
- `get_current_user` - Get current user info
- `get_assignable_users_for_project` - Get assignable users for a project
- `get_assignable_users_for_issue` - Get assignable users for an issue

## Development Commands

- `make build` - Build the Podman image
- `make run` - Run the container (requires JIRA_API_TOKEN env var)
- `make test` - Test the server
- `make clean` - Clean up Podman images

## Troubleshooting

### Server Not Starting
- Ensure Podman is running
- Check that the JIRA_API_TOKEN is correct
- Verify the Podman image was built successfully with `podman images | grep jira-mcp`

### Connection Issues
- Restart Cursor after configuration changes
- Check Cursor's developer console for error messages
- Verify the Jira URL is accessible from your network

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
