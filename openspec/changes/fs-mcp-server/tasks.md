## 1. Path containment

- [ ] 1.1 Add `fsmcp/safe_path.py` with `_safe_resolve(root, path) -> Path`: join, `realpath`, reject unless `is_relative_to(root)`
- [ ] 1.2 Self-check (`test_*.py` or `__main__` asserts): `..` escape, absolute path outside root, and symlink-out-of-root all raise; in-root paths pass

## 2. Filesystem server

- [ ] 2.1 Add `fsmcp/server.py`: build an `mcp` stdio server; read root from argv/env and exit if it is not an existing directory
- [ ] 2.2 Implement `list_dir(path)`: `_safe_resolve`, require a directory, return entries tagged file/dir; non-dir/missing → MCP error
- [ ] 2.3 Implement `read_file(path)`: `_safe_resolve`, require a file, read ≤ `MAX_READ_BYTES`, UTF-8 decode (`errors="replace"`), flag truncation; non-file/missing → MCP error
- [ ] 2.4 Add `fsmcp/__main__.py` so `python -m fsmcp <root>` runs the stdio server

## 3. Wire into the bridge

- [ ] 3.1 Add an example `fsmcp` upstream to `config.example.yaml` (`python -m fsmcp <root>`) and allowlist `list_dir` + `read_file`
- [ ] 3.2 Verify: bridge spawns `fsmcp`, `tools/list` shows only the two allowlisted tools, a `read_file` of an in-root file returns its text

## 4. Docs

- [ ] 4.1 README: note the read-only fs server, its root arg, and that it can read anything under that root with the bridge's privileges
