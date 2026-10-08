# Level 10 · MCP Tools

**Big idea:** the **Model Context Protocol** is one standard way to plug tools and data into any agent. Write a tool server once; every MCP client (your agent, Claude Desktop, Claude Code, IDEs) can use it. MCP is now under vendor-neutral governance at the Linux Foundation.

**Ops Buddy gains:** uses a ticketing and calendar server, and exposes its own leave tools to other apps.

## The examples

| File | What it shows | Needs API key |
|---|---|---|
| `leave_server.py` | Ops Buddy's leave tools + a resource, as an MCP server | (server) |
| `helpdesk_server.py` | "Someone else's" server: tickets + team calendar | (server) |
| `01_mcp_client.py` | Start a server, list tools and resources, call a tool, with no LLM | **No** |
| `02_agent_with_mcp.py` | `create_agent` with tools loaded from both servers | Yes |

## How it fits

```
                 ┌──────────────────┐  stdio / HTTP   ┌──────────────────┐
  Ops Buddy ───▶ │ MCP client       │ ◀─────────────▶ │ leave_server     │  (we wrote it)
  (agent)        │ (langchain-mcp-  │                 └──────────────────┘
                 │  adapters)       │ ◀─────────────▶ ┌──────────────────┐
                 └──────────────────┘                 │ helpdesk_server  │  (Jira, Calendar...)
                                                      └──────────────────┘
  Claude Desktop / Claude Code / IDE ──────────────▶ leave_server (same server, no changes)
```

## MCP's three building blocks

| | What | Example here |
|---|---|---|
| **Tools** | functions the model can call | `apply_leave`, `team_calendar` |
| **Resources** | data the app can read | `policy://leave` |
| **Prompts** | reusable prompt templates | (not used here) |

## Expose Ops Buddy to other apps

```bash
claude mcp add ops-buddy-leave -- python /full/path/to/level-10-mcp/leave_server.py
```

Then ask Claude Code: "How many casual leaves does E1042 have?"

## Try it

1. Add a `cancel_leave` tool to `leave_server.py`. Re-run `01`: it appears with no client changes.
2. In `02`, remove the helpdesk server. How does the agent's answer change?
3. MCP servers run with real permissions. Which tool in these servers would you *not* want any app to call? (Level 13.)
