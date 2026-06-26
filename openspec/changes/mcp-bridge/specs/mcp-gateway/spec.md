## ADDED Requirements

### Requirement: Connect to configured upstream MCP servers
The gateway SHALL launch and connect to each local stdio MCP server listed in its
configuration, and SHALL discover the tools each server exposes.

#### Scenario: Upstream server starts and tools are discovered
- **WHEN** the gateway starts with one configured upstream stdio server
- **THEN** it spawns that server, completes the MCP initialize handshake, and lists its tools

#### Scenario: Multiple upstream servers
- **WHEN** the configuration lists more than one upstream server
- **THEN** the gateway connects to all of them and aggregates their tools into one tool list

### Requirement: Expose tools over Streamable HTTP transport
The gateway SHALL act as an MCP server reachable over the MCP Streamable HTTP transport so a
remote cloud assistant can list tools and call them.

#### Scenario: Remote client lists tools
- **WHEN** an authenticated remote client sends `tools/list` to the gateway's HTTP endpoint
- **THEN** the gateway responds with the aggregated, allowlisted tool definitions

### Requirement: Proxy tool calls to the owning upstream server
The gateway SHALL route each `tools/call` to the upstream server that owns the named tool and
SHALL return that server's result (or error) to the remote client unchanged.

#### Scenario: Tool call is proxied and result returned
- **WHEN** a remote client calls an allowlisted tool
- **THEN** the gateway forwards the call to the owning upstream server and returns its result

#### Scenario: Unknown tool name
- **WHEN** a remote client calls a tool that no upstream server owns
- **THEN** the gateway returns an MCP error and does not crash

### Requirement: Survive upstream failure
The gateway SHALL remain available to the remote client if an upstream server exits or errors,
reporting a tool-level error rather than terminating the public endpoint.

#### Scenario: Upstream crashes mid-session
- **WHEN** an upstream server process dies while the gateway is serving requests
- **THEN** calls to that server's tools return an error and the gateway keeps serving other tools
