# redhat-ai-tools/jira-mcp

A containerized Python MCP server for Cursor to provide access to Jira.

> [!IMPORTANT]
> This project is experimental and was initially created as a learning exercise.
> Be aware there are more capable and mature Jira MCP solutions available,
> such as [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian),
> and Atlassian's own [MCP Server](https://www.atlassian.com/platform/remote-mcp-server).

See also [redhat-ai-tools/jira-mcp-snowflake](https://github.com/redhat-ai-tools/jira-mcp-snowflake)
which provides another way to access Red Hat Jira data.

## Prerequisites

- **podman** - Install with `sudo dnf install podman` (Fedora/RHEL) or `brew install podman` (macOS)
- **make** - Usually pre-installed on most systems
- **yq** - Install with `brew install yq` (macOS)

## Quick Start

1. **Get the code**
  ```bash
  git clone git@github.com:redhat-ai-tools/jira-mcp.git
  cd jira-mcp
  ```
2. **Build the image & configure Cursor**<br>
  This also creates a `~/.rh-jira-mcp.env` file like [this](example.env).
  ```bash
  make setup
  ```

3. **Prepare a Jira token**
   * Go to [Red Hat Jira Personal Access Tokens](https://issues.redhat.com/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens) and create a token
   * Edit the `.rh-jira-mcp.env` file in your home directory and paste in the token

To confirm it's working, run Cursor, go to Settings and click on "Tools &
Integrations". Under MCP Tools you should see "jiraMcp" with 20 tools enabled.

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

- `make build` - Build the image
- `make run` - Run the container
- `make clean` - Clean up the built image
- `make cursor-config` - Modify `~/.cursor/mcp.json` to install this MCP Server
- `make setup` - Builds the image, configures Cursor, and creates `~/.rh-jira-mcp.env` if it doesn't exist

## Troubleshooting

### Server Not Starting
- Confirm that `make run` works
- Check that the JIRA_API_TOKEN is correct
- Verify the image was built successfully with `podman images jira-mcp`
- Go to the "Output" tab in Cursor's bottom pane, choose "MCP Logs" from the drop-down select and examine the logs there

### Connection Issues
- Restart Cursor after configuration changes
- Check Cursor's developer console for error messages
- Verify the Jira URL is accessible from your network

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
