## Context

The bridge (see `mcp-bridge`) spawns stdio MCP servers and re-exposes selected tools over HTTPS,
but the repo ships no actual upstream to point it at. This change adds the first one: a tiny
read-only filesystem server. It runs as a stdio subprocess of the bridge, so the bridge's bearer
token and allowlist already gate remote access — this server's own job is only to stay inside its
root and never mutate anything.

Constraints: single-language stack (Python), no new dependency (the `mcp` SDK is already in
`pyproject.toml`), and the per-file 100-line / 10-line house style.

## Goals / Non-Goals

**Goals:**
- A stdio MCP server with two tools — `list_dir`, `read_file` — confined to one root directory.
- Path containment that holds against `..`, absolute paths, and symlinks, enforced in one place.
- Runs unmodified as a bridge upstream; wired into the example config.

**Non-Goals:**
- Writing, moving, or deleting files (read-only by design).
- Search / glob / recursive walk / file watching — add later if a real need shows up.
- Binary file handling beyond a UTF-8 decode with a size cap; no streaming, no ranges.
- Its own auth — the bridge owns the trust boundary.

## Decisions

### Reuse the `mcp` SDK's stdio server
Use the already-installed `mcp` SDK (`mcp.server` + stdio transport) rather than hand-rolling JSON-RPC.
Rung 4 of the ladder: the dependency is already here. Alternative (raw stdio JSON-RPC loop) is more
code and re-implements the handshake for no gain.

### Exactly two tools
`list_dir(path)` → entries tagged file/dir; `read_file(path)` → UTF-8 text. "Browse my files" needs
list + read and nothing more. `stat`, `glob`, recursive walk are YAGNI — the directory listing
already carries type info. Add when a caller actually needs them.

### One containment chokepoint
A single `_safe_resolve(path) -> Path` helper does: join the request path onto the root, `realpath`
it (which also collapses symlinks), and reject unless the result is the root or a descendant
(`Path.is_relative_to(root)`). Both tools call it before touching the filesystem, so traversal,
absolute-path, and symlink escapes are all refused at the same gate. Resolving *before* reading means
an out-of-root path never reaches an `open()`. Alternative (string-prefix checks on the raw path) is
fragile against symlinks and `..` normalization — rejected.

### Read cap as a constant
`read_file` reads at most `MAX_READ_BYTES` (e.g. 1 MiB) and flags truncation in the response. A plain
module constant, not config — there's no second value anyone needs yet. (`ponytail:` constant, promote
to config when a caller needs a different cap.)

### Root from a CLI arg / env, validated at startup
The bridge passes the root as an argument (it spawns the command); the server validates it is an
existing directory and exits otherwise (fail fast, mirroring the bridge's fail-closed posture).

## Risks / Trade-offs

- **TOCTOU between resolve and open** → For a read-only server the worst case is reading a file that
  was swapped under a symlink after the check; acceptable, and the resolve-then-open ordering keeps the
  window tiny. Note it; don't build locking for a read-only path.
- **UTF-8 decode fails on binary files** → `read_file` decodes with `errors="replace"` so a binary
  file returns lossy text rather than crashing; callers wanting raw bytes are out of scope.
- **Symlinks pointing *into* the root** → still allowed (target is inside root); that's intended, the
  check is about the resolved target, not whether a symlink was traversed.

## Open Questions

- Should `list_dir` hide dotfiles by default? Leaning no (show everything under the root, it's the
  user's own tree) — revisit if noisy.
