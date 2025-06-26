# redhat-ai-tools/jira-mcp

For use with Cursor to provide access to Jira.

> [!IMPORTANT]
> This project is experimental and was initially created as a learning exercise.
> Be aware there are more capable and mature Jira MCP solutions available,
> such as [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian),
> and Atlassian's own [MCP Server](https://www.atlassian.com/platform/remote-mcp-server).

## Cursor config

Example configuration file for Cursor, probably in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "jira-mcp": {
      "command": "/some/path/jira-mcp/server.sh",
      "description": "A simple MCP server to query Jira issues"
    }
  }
}
```

## Getting started

* Run `make setup` to set up a python venv environment and install
  the dependencies.
* (Optional) Run `source .venv/bin/activate` to set the venv python
  path in your terminal.
* Go to your Jira profile page and create a personal access token, for
  example [here][rh-token-page].
* Copy `.env.example` to `.env`, add your token to that file, and update
  the url as required.
* Go to "Tools & Integrations" in the Cursor settings and paste in the JSON
  from above. Adjust the command path as required.
* If it's working you should see a green indicator and "1 tools enabled".
* You should then be able to refer to Jiras in the Cursor AI pane, e.g.
  "summarize the requirements for jira EC-1332".

[rh-token-page]: https://issues.redhat.com/secure/ViewProfile.jspa?selectedTab=com.atlassian.pats.pats-plugin:jira-user-personal-access-tokens

## Notes

* The instructions above assume you want to use
  [venv](https://docs.python.org/3/library/venv.html).
  You can use system python if you prefer.
  Do a `pip install -r requirements.txt` and adjust
  `server.sh` as required.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
