# mcp-server

For use with Cursor to provide access to Jira.

Example configuration file for Cursor (probably in `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/home/sbaird/code/mcp-server/server.sh",
      "description": "A simple MCP server to query Jira issues"
    }
  }
}
```

## Getting started

* Run `make setup` to set up the python environment
* (Optional) Run `source venv/bin/activate` to set the python path
* Create a [Jira token here][jira-token]
* Copy `.env.example` to `.env` and add your token to that file
* Go to "Tools & Integrations" in the Cursor settings and paste in the JSON
   from above. Adjust the paths as appropriate.

[jira-token]: https://issues.redhat.com/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens