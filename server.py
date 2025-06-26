#!/usr/bin/env python

import os
from dotenv import load_dotenv
from jira import JIRA
from fastmcp import FastMCP
from fastapi import HTTPException

# ─── 1. Load environment variables ─────────────────────────────────────────────
load_dotenv()

JIRA_URL       = os.getenv("JIRA_URL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

if not all([JIRA_URL, JIRA_API_TOKEN]):
    raise RuntimeError("Missing JIRA_URL or JIRA_API_TOKEN in .env")

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

# ─── 5. Run the HTTP-based MCP server on port 8000 ───────────────────────────────
if __name__ == "__main__":
    print(f"Using JIRA_URL={JIRA_URL}")
    mcp.run()
