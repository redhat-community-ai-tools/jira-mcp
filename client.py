#!/usr/bin/env python3
import asyncio
import argparse
import sys
import json
import traceback
from mcp.client.streamable_http import streamable_http_client
from mcp.client.session import ClientSession

# Default URL for FastMCP HTTP (Streamable) transport
SERVER_URL = "http://localhost:8080/mcp"


async def run_mcp_tool(tool_name, arguments):
    print(f"Connecting to {SERVER_URL}...", file=sys.stderr)
    try:
        async with streamable_http_client(SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                print("Initializing session...", file=sys.stderr)
                await session.initialize()

                print(
                    f"Calling tool '{tool_name}' with args: {json.dumps(arguments)}",
                    file=sys.stderr,
                )
                result = await session.call_tool(tool_name, arguments=arguments)
                return result
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        print(f"Error during MCP communication: {e}", file=sys.stderr)
        return None


async def main():
    parser = argparse.ArgumentParser(description="Simple Jira MCP Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search Command
    search_parser = subparsers.add_parser("search", help="Search issues using JQL")
    search_parser.add_argument("jql", help="JQL query string")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")

    # Get Command
    get_parser = subparsers.add_parser("get", help="Get detailed issue info")
    get_parser.add_argument("key", help="Issue Key (e.g., TEST-123)")
    get_parser.add_argument("--extra", nargs="+", default=[], help="List of extra fields to fetch")

    # Create Command
    create_parser = subparsers.add_parser("create", help="Create a new issue")
    create_parser.add_argument("summary", help="Issue Summary")
    create_parser.add_argument("--project", required=True, help="Project Key")
    create_parser.add_argument("--desc", default="", help="Description")
    create_parser.add_argument("--type", default="Task", help="Issue Type")
    create_parser.add_argument("--priority", help="Priority")
    create_parser.add_argument("--assignee", help="Assignee username")
    # Example of hardcoded/flexible extra fields
    create_parser.add_argument("--labels", nargs="+", help="Labels to add (example of extra field)")

    # Update Command
    update_parser = subparsers.add_parser("update", help="Update an existing issue")
    update_parser.add_argument("key", help="Issue Key (e.g., TEST-123)")
    update_parser.add_argument("--summary", help="New Summary")
    update_parser.add_argument("--desc", help="New Description")
    update_parser.add_argument("--priority", help="New Priority")
    update_parser.add_argument("--assignee", help="New Assignee")

    args = parser.parse_args()

    if args.command == "search":
        tool_name = "search_issues"
        arguments = {
            "jql": args.jql,
            "max_results": args.limit,
            "extra_fields": [
                "customfield_12313140",
                "customfield_12311140",
                "customfield_12310243",
            ],
        }

    elif args.command == "get":
        tool_name = "get_jira"
        arguments = {"issue_key": args.key, "extra_fields": args.extra}

    elif args.command == "create":
        tool_name = "create_issue"
        arguments = {
            "project_key": args.project,
            "summary": args.summary,
            "description": args.desc,
            "issue_type": args.type,
            "priority": args.priority,
        }
        if args.assignee:
            arguments["assignee"] = args.assignee

        # Demonstrate usage of extra_fields
        extra_fields = {}
        if args.labels:
            extra_fields["labels"] = args.labels

        if extra_fields:
            arguments["extra_fields"] = extra_fields

    elif args.command == "update":
        tool_name = "update_issue"
        arguments = {"issue_key": args.key}
        if args.summary:
            arguments["summary"] = args.summary
        if args.desc:
            arguments["description"] = args.desc
        if args.priority:
            arguments["priority"] = args.priority
        if args.assignee:
            arguments["assignee"] = args.assignee

    # Execute
    result = await run_mcp_tool(tool_name, arguments)

    if result:
        print("\n--- Result ---\n")
        # Handle different content types if necessary, but usually it's TextContent
        for content in result.content:
            if hasattr(content, "text"):
                print(content.text)
            else:
                print(str(content))
    else:
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
