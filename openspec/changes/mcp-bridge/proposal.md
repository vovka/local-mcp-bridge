## Why

Cloud AI assistants (ChatGPT, Claude) can call remote MCP servers over HTTPS, but the
useful tools — browser automation, local files, dev tooling — run on the user's laptop
behind no public address. Today there is no safe, self-hosted way to let a cloud assistant
reach those local tools without exposing the whole machine. This change ships a local-first
bridge that publishes *selected* local MCP tools through a single authenticated public
HTTPS endpoint.

## What Changes

- Add an MCP **gateway server** that connects to one or more local stdio MCP servers
  (e.g. browser automation) and re-exposes their tools over the MCP Streamable HTTP transport
  that cloud assistants speak.
- Add **access control**: a bearer token on the public endpoint plus a per-tool allowlist so
  only explicitly selected tools are reachable; everything else is hidden and refused.
- Add **deployment**: a Docker container that runs the gateway and opens an ngrok HTTPS tunnel,
  configured entirely from environment variables / a single config file.
- No changes to the local MCP servers themselves — they are consumed as-is.

## Capabilities

### New Capabilities
- `mcp-gateway`: Bridge between local stdio MCP servers and the remote MCP Streamable HTTP
  transport — connect to configured upstream servers, aggregate their tools, and proxy
  tool calls in both directions.
- `access-control`: Authenticate remote clients with a bearer token and enforce a per-tool
  allowlist so only selected tools are exposed.
- `deployment`: Package the gateway in Docker and expose it publicly via an ngrok HTTPS tunnel,
  driven by a single config file / env vars.

### Modified Capabilities
<!-- None — greenfield project, no existing specs. -->

## Impact

- New project code (gateway server + config). No existing code to modify (greenfield).
- Dependencies: an MCP SDK (server + stdio client transport), ngrok, Docker.
- Runtime surface: one public HTTPS endpoint (ngrok) → gateway → local stdio MCP processes.
- Security surface: the public endpoint is the trust boundary — auth and allowlist live there.
