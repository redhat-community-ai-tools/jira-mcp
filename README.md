# mcp-server

For use with Cursor to provide access to Jira.

> [!NOTE]
> This project is experimental and was initially created as a learning exercise.
> Be aware there are more capable and mature Jira MCP solutions available,
> such as [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian),
> and Atlasian's own [MCP Server](https://www.atlassian.com/platform/remote-mcp-server).

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
   from above. Adjust the path as appropriate.
* If it's working you should see a green indicator and "1 tools enabled"
* You should then be able to refer to Jiras in the chat panel, e.g. "What is
   jira EC-1324 about"

[jira-token]: https://issues.redhat.com/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens
