#!/usr/bin/env python

import os
import argparse
from dotenv import load_dotenv
from jira import JIRA
from fastmcp import FastMCP
from fastapi import HTTPException
import json
import logging

## Custom fields IDs
QA_CONTACT_FID = "customfield_12315948"

# ─── 1. Load environment variables ─────────────────────────────────────────────
load_dotenv()

JIRA_URL       = os.getenv("JIRA_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_ENABLE_WRITE_OPERATIONS_STRING = os.getenv("JIRA_ENABLE_WRITE", "false")
ENABLE_WRITE = JIRA_ENABLE_WRITE_OPERATIONS_STRING.lower() == "true"

if not all([JIRA_URL, JIRA_API_TOKEN]):
    raise RuntimeError("Missing JIRA_URL or JIRA_API_TOKEN environment variables")

# ─── 2. Create a Jira client ───────────────────────────────────────────────────
#    Uses token_auth (API token) for authentication.
jira_client = JIRA(server=JIRA_URL, token_auth=JIRA_API_TOKEN)

# ─── 3. Instantiate the MCP server ─────────────────────────────────────────────
mcp = FastMCP("Jira Context Server")

# ─── 4. Register the get_jira tool ─────────────────────────────────────────────
@mcp.tool()
def get_jira(issue_key: str) -> str:
    """
    Fetch the Jira issue identified by 'issue_key' using jira_client,
    then return a Markdown string: "# ISSUE-KEY: summary\n\ndescription"
    """
    try:
        issue = jira_client.issue(issue_key)
    except Exception as e:
        # If the JIRA client raises an error (e.g. issue not found),
        # wrap it in an HTTPException so MCP/Client sees a 4xx/5xx.
        raise HTTPException(status_code=404, detail=f"Failed to fetch Jira issue {issue_key}: {e}")

    # Extract summary & description fields
    summary     = issue.fields.summary or ""
    description = issue.fields.description or ""

    return f"# {issue_key}: {summary}\n\n{description}"

def to_markdown(obj):
    if isinstance(obj, dict):
        return '```json\n' + json.dumps(obj, indent=2) + '\n```'
    elif hasattr(obj, 'raw'):
        return '```json\n' + json.dumps(obj.raw, indent=2) + '\n```'
    elif isinstance(obj, list):
        return '\n'.join([to_markdown(o) for o in obj])
    else:
        return str(obj)

@mcp.tool()
def search_issues(jql: str, max_results: int = 100) -> str:
    """Search issues using JQL."""
    try:
        issues = jira_client.search_issues(jql, maxResults=max_results)
        # Extract only essential fields to avoid token limit issues
        simplified_issues = []
        for issue in issues:
            simplified = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'status': issue.fields.status.name if issue.fields.status else None,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'qa_contact': getattr(issue.fields, QA_CONTACT_FID).displayName if getattr(issue.fields, QA_CONTACT_FID) else None,
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                'priority': issue.fields.priority.name if issue.fields.priority else None,
                'issuetype': issue.fields.issuetype.name if issue.fields.issuetype else None,
                'fixVersion': issue.fields.fixVersions[0].name if issue.fields.fixVersions else None,
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'description': issue.fields.description
            }
            simplified_issues.append(simplified)
        return to_markdown(simplified_issues)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JQL search failed: {e}")

@mcp.tool()
def search_users(query: str, max_results: int = 10) -> str:
    """Search users by query."""
    try:
        users = jira_client.search_users(query, maxResults=max_results)
        return to_markdown([u.raw for u in users])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to search users: {e}")

@mcp.tool()
def list_projects() -> str:
    """List all projects."""
    try:
        projects = jira_client.projects()
        return to_markdown([p.raw for p in projects])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch projects: {e}")

@mcp.tool()
def get_project(project_key: str) -> str:
    """Get a project by key."""
    try:
        project = jira_client.project(project_key)
        return to_markdown(project)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch project: {e}")

@mcp.tool()
def get_project_components(project_key: str) -> str:
    """Get components for a project."""
    try:
        components = jira_client.project_components(project_key)
        return to_markdown([c.raw for c in components])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch components: {e}")

@mcp.tool()
def get_project_versions(project_key: str) -> str:
    """Get versions for a project."""
    try:
        versions = jira_client.project_versions(project_key)
        return to_markdown([v.raw for v in versions])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch versions: {e}")

@mcp.tool()
def get_project_roles(project_key: str) -> str:
    """Get roles for a project."""
    try:
        roles = jira_client.project_roles(project_key)
        return to_markdown(roles)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch roles: {e}")

@mcp.tool()
def get_project_permission_scheme(project_key: str) -> str:
    """Get permission scheme for a project."""
    try:
        scheme = jira_client.project_permissionscheme(project_key)
        return to_markdown(scheme.raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch permission scheme: {e}")

@mcp.tool()
def get_project_issue_types(project_key: str) -> str:
    """Get issue types for a project."""
    try:
        types = jira_client.project_issue_types(project_key)
        return to_markdown([t.raw for t in types])
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch issue types: {e}")

@mcp.tool()
def get_current_user() -> str:
    """Get current user info."""
    try:
        user = jira_client.myself()
        return to_markdown(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch current user: {e}")

@mcp.tool()
def get_user(account_id: str) -> str:
    """Get user by account ID."""
    try:
        user = jira_client.user(account_id)
        return to_markdown(user.raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch user: {e}")

@mcp.tool()
def get_assignable_users_for_project(project_key: str, query: str = "", max_results: int = 10) -> str:
    """Get assignable users for a project."""
    try:
        users = jira_client.search_assignable_users_for_projects(query, project_key, maxResults=max_results)
        return to_markdown([u.raw for u in users])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get assignable users: {e}")

@mcp.tool()
def get_assignable_users_for_issue(issue_key: str, query: str = "", max_results: int = 10) -> str:
    """Get assignable users for an issue."""
    try:
        users = jira_client.search_assignable_users_for_issues(query, issueKey=issue_key, maxResults=max_results)
        return to_markdown([u.raw for u in users])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get assignable users: {e}")

@mcp.tool()
def list_boards(max_results: int = 10, project_key_or_id: str = None) -> str:
    """List boards, optionally filtered by project."""
    try:
        boards = jira_client.boards(maxResults=max_results, projectKeyOrID=project_key_or_id)
        return to_markdown([b.raw for b in boards])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch boards: {e}")

@mcp.tool()
def list_sprints(board_id: int, max_results: int = 10) -> str:
    """List sprints for a board."""
    try:
        sprints = jira_client.sprints(board_id, maxResults=max_results)
        return to_markdown([s.raw for s in sprints])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sprints: {e}")

@mcp.tool()
def get_sprint(sprint_id: int) -> str:
    """Get sprint by ID."""
    try:
        sprint = jira_client.sprint(sprint_id)
        return to_markdown(sprint.raw)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to fetch sprint: {e}")

@mcp.tool()
def get_sprints_by_name(board_id: int, state: str = None) -> str:
    """Get sprints by name for a board, optionally filtered by state."""
    try:
        sprints = jira_client.sprints_by_name(board_id, state=state)
        return to_markdown(sprints)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sprints by name: {e}")

# ─── 5. Write Operations ───────────────────────────────────────────────────────

@mcp.tool(enabled=ENABLE_WRITE)
def create_issue(project_key: str, summary: str, description: str = "", issue_type: str = "Task", priority: str = "Medium", assignee: str = None) -> str:
    """Create a new Jira issue."""
    try:
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            'priority': {'name': priority}
        }

        if assignee:
            issue_dict['assignee'] = {'name': assignee}

        new_issue = jira_client.create_issue(fields=issue_dict)
        return f"Created issue {new_issue.key}: {summary}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create issue: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def update_issue(issue_key: str, summary: str = None, description: str = None, priority: str = None, assignee: str = None) -> str:
    """Update an existing Jira issue."""
    try:
        issue = jira_client.issue(issue_key)
        update_dict = {}

        if summary:
            update_dict['summary'] = summary
        if description:
            update_dict['description'] = description
        if priority:
            update_dict['priority'] = {'name': priority}
        if assignee:
            update_dict['assignee'] = {'name': assignee}

        if update_dict:
            issue.update(fields=update_dict)
            return f"Updated issue {issue_key} successfully"
        else:
            return f"No updates provided for issue {issue_key}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update issue {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def add_comment(issue_key: str, comment_body: str) -> str:
    """Add a comment to a Jira issue."""
    try:
        issue = jira_client.issue(issue_key)
        comment = jira_client.add_comment(issue, comment_body)
        return f"Added comment to {issue_key}: {comment.id}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add comment to {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def delete_comment(issue_key: str, comment_id: str) -> str:
    """Delete a comment from a Jira issue."""
    try:
        comment = jira_client.comment(issue_key, comment_id)
        comment.delete()
        return f"Deleted comment {comment_id} from {issue_key}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete comment {comment_id} from {issue_key}: {e}")

@mcp.tool()
def get_issue_comments(issue_key: str) -> str:
    """Get all comments for a Jira issue."""
    try:
        issue = jira_client.issue(issue_key)
        comments = []
        for comment in issue.fields.comment.comments:
            comment_data = {
                'id': comment.id,
                'author': comment.author.displayName if comment.author else 'Unknown',
                'body': comment.body,
                'created': comment.created,
                'updated': comment.updated if hasattr(comment, 'updated') else comment.created
            }
            comments.append(comment_data)
        return to_markdown(comments)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get comments for {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def assign_issue(issue_key: str, assignee: str) -> str:
    """Assign a Jira issue to a user."""
    try:
        issue = jira_client.issue(issue_key)
        jira_client.assign_issue(issue, assignee)
        return f"Assigned issue {issue_key} to {assignee}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to assign issue {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def unassign_issue(issue_key: str) -> str:
    """Unassign a Jira issue."""
    try:
        issue = jira_client.issue(issue_key)
        jira_client.assign_issue(issue, None)
        return f"Unassigned issue {issue_key}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to unassign issue {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def transition_issue(issue_key: str, transition_name: str, comment: str = None) -> str:
    """Transition a Jira issue to a new status."""
    try:
        issue = jira_client.issue(issue_key)
        transitions = jira_client.transitions(issue)

        # Find the transition by name
        transition_id = None
        for trans in transitions:
            if trans['name'].lower() == transition_name.lower():
                transition_id = trans['id']
                break

        if not transition_id:
            available_transitions = [t['name'] for t in transitions]
            return f"Transition '{transition_name}' not found. Available transitions: {', '.join(available_transitions)}"

        # Perform the transition
        if comment:
            jira_client.transition_issue(issue, transition_id, comment=comment)
            return f"Transitioned issue {issue_key} to '{transition_name}' with comment"
        else:
            jira_client.transition_issue(issue, transition_id)
            return f"Transitioned issue {issue_key} to '{transition_name}'"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to transition issue {issue_key}: {e}")

@mcp.tool()
def get_issue_transitions(issue_key: str) -> str:
    """Get available transitions for a Jira issue."""
    try:
        issue = jira_client.issue(issue_key)
        transitions = jira_client.transitions(issue)
        transition_list = [{'id': t['id'], 'name': t['name']} for t in transitions]
        return to_markdown(transition_list)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get transitions for {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def delete_issue(issue_key: str) -> str:
    """Delete a Jira issue (use with caution)."""
    try:
        issue = jira_client.issue(issue_key)
        issue.delete()
        return f"Deleted issue {issue_key}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete issue {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def add_issue_labels(issue_key: str, labels: list) -> str:
    """Add labels to a Jira issue."""
    try:
        issue = jira_client.issue(issue_key)
        current_labels = list(issue.fields.labels)
        new_labels = list(set(current_labels + labels))  # Remove duplicates
        issue.update(fields={'labels': new_labels})
        return f"Added labels {labels} to issue {issue_key}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add labels to {issue_key}: {e}")

@mcp.tool(enabled=ENABLE_WRITE)
def remove_issue_labels(issue_key: str, labels: list) -> str:
    """Remove labels from a Jira issue."""
    try:
        issue = jira_client.issue(issue_key)
        current_labels = list(issue.fields.labels)
        new_labels = [label for label in current_labels if label not in labels]
        issue.update(fields={'labels': new_labels})
        return f"Removed labels {labels} from issue {issue_key}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to remove labels from {issue_key}: {e}")

# ─── 6. Utility functions ─────────────────────────────────────────────────────
def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Jira Context Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""

Environment Variables:
  JIRA_API_TOKEN: Your Jira API token.

Examples:
  python server.py                                 # Run with stdio
  python server.py --transport http                # Streamable HTTP server mode
  python server.py --transport sse                 # SSE HTTP server mode (deprecated)
  python server.py --transport sse --port 8080     # Custom port
  python server.py --transport sse --host 0.0.0.0  # Bind to all interfaces

  # With API token
  JIRA_API_TOKEN=your_api_key_here python server.py
        """
    )

    parser.add_argument(
        "--transport", "-t",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport mode: stdio (default) or http (streamable HTTP-based server) or sse (deprecated HTTP-based server)"
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to in HTTP mode (default: localhost)"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=3000,
        help="Port to bind to in HTTP mode (default: 3000)"
    )

    return parser.parse_args()


# ─── 7. Run the MCP server  ───────────────────────────────

if __name__ == "__main__":
    args = parse_arguments()

    if args.transport == "stdio":
        mcp.run(transport=args.transport)
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port)
