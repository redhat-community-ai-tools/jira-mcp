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

4. **Decide whether to enable write operations**

Enabling your MCP server to make edits to Jira can be very useful, but can also cause a lot of problems if you are not careful in how you use the MCP tools.
By default, the server has write operations turned off.
If you want to turn it on, edit the `.rh-jira-mcp.env` file in your home directory to set `JIRA_ENABLE_WRITE_OPERATIONS=true`.

5. **Check if it is working in Cursor**

To confirm it's working, run Cursor, go to Settings and click on "Tools & Integrations". Under MCP Tools you should see "jiraMcp" with 20 tools enabled if 
`JIRA_ENABLE_WRITE_OPERATIONS=false` (the default value) or 30 tools enabled if `JIRA_ENABLE_WRITE_OPERATIONS=true`.

## Using with an HTTP-based MCP application

If you want to use this MCP server with an application that communicates via HTTP, then you need to run the server with an HTTP-based transport mechanism.
Here is an example of how to do this using Streamable HTTP, which is the current recommended http-based transport mechanism for MCP:

```
export $(grep -v '^#' ~/.rh-jira-mcp.env | xargs) && python server.py --transport http --port 3075
```

Here is an example of how to do this using SSE, which is a deprecated http-based transport mechanism (e.g., because you have an older MCP client application that depends on SSE):

```
export $(grep -v '^#' ~/.rh-jira-mcp.env | xargs) && python server.py --transport sse --port 3075
```

## Available Tools

This MCP server provides the following tools:

### Issue Search & Retrieval
- `get_jira` - Get details for a specific Jira issue by key.
- `search_issues` - Search issues using JQL

### Issue Creation & Management
- `create_issue` - Create a new Jira issue with summary, description, type, priority, and assignee
- `update_issue` - Update an existing issue's summary, description, priority, or assignee
- `delete_issue` - Delete a Jira issue (use with caution)

### Issue Comments
- `get_issue_comments` - Get all comments for a Jira issue
- `add_comment` - Add a comment to a Jira issue
- `delete_comment` - Delete a comment from a Jira issue

### Issue Assignment
- `assign_issue` - Assign a Jira issue to a user
- `unassign_issue` - Unassign a Jira issue

### Issue Workflow & Status
- `transition_issue` - Transition a Jira issue to a new status (e.g., "In Progress", "Done")
- `get_issue_transitions` - Get available transitions for a Jira issue

### Issue Labels
- `add_issue_labels` - Add labels to a Jira issue
- `remove_issue_labels` - Remove labels from a Jira issue

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
- `list_sprints` - List sprints for a board
- `get_sprint` - Get sprint details by ID
- `get_sprints_by_name` - Get sprints by name for a board, optionally filtered by state

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
- (MacOS) jiraMcp shows up in Cursor tools section but shows no active tools:
  - Edit args section of jiraMcp of your `mcp.json` file to include your full path to the `.rh-jira-mcp.env` file.
  - Example: `"~/.rh-jira-mcp.env",` to `"/Users/your_username/.rh-jira-mcp.env",`

### Connection Issues
- Restart Cursor after configuration changes
- Check Cursor's developer console for error messages
- Verify the Jira URL is accessible from your network

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
