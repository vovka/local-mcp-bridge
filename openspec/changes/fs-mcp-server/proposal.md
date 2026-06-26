## Why

The bridge can publish local stdio MCP tools to cloud assistants, but the obvious thing
a remote assistant wants — *look at my files* — has no local server in this repo to point
it at. We need a small, in-repo stdio MCP server that lets a cloud assistant browse and read
files under one directory, so the bridge has a first real upstream to expose (and a worked
example of the upstream contract).

## What Changes

- Add a **read-only filesystem MCP server** (`fsmcp`) that runs as a stdio MCP subprocess and
  exposes two tools: `list_dir` (entries under a path) and `read_file` (text contents of a file).
- The server is **rooted at one configured base directory**: every path is resolved and confined
  to that root; requests that escape it (`..`, absolute paths, symlinks out of root) are refused.
- It is **read-only**: no write, move, or delete tools. `read_file` caps the bytes returned so a
  huge file can't blow up the response.
- Wire it into `config.example.yaml` as an example upstream with `list_dir` / `read_file`
  allowlisted, so the bridge spawns and re-exposes it end-to-end.
- Reuses the `mcp` SDK already in `pyproject.toml` — **no new dependency**, no new runtime.

## Capabilities

### New Capabilities
- `fs-browse`: A read-only stdio MCP server that lists directories and reads text files within a
  single configured root, with path-traversal containment and a read size cap.

### Modified Capabilities
<!-- None — the bridge consumes this as an ordinary upstream; no existing requirement changes. -->

## Impact

- New code: a small `fsmcp/` stdio server (uses the existing `mcp` SDK). One self-check for the
  path-containment logic.
- Config: `config.example.yaml` / `config.yaml` gain an example `fsmcp` upstream + allowlist entries.
- Security surface: this process can read any file under its root with the bridge's privileges —
  the root directory and the allowlist are the trust boundary. Confinement and read-only are
  load-bearing, not conveniences.
- Alternative considered: the official `@modelcontextprotocol/server-filesystem` (Node) would
  need no code, but pulls in a Node runtime and is read/write; an in-repo read-only Python server
  keeps the stack single-language and the blast radius minimal.
