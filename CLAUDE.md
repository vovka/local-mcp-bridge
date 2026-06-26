# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A local-first gateway that exposes **selected** local stdio MCP tools (e.g. browser automation)
to cloud AI assistants (Claude, ChatGPT) over one authenticated public HTTPS endpoint:

```
local stdio MCP servers ─▶ bridge (MCP Streamable HTTP) ─▶ ngrok HTTPS ─▶ cloud assistant
```

The bridge connects to upstream stdio MCP servers as a client, re-exposes their tools as an MCP
Streamable HTTP server, and ngrok publishes that endpoint. **A bearer token plus a per-tool
allowlist are the only trust boundary.**

**Current state: scaffold.** The config loader (`bridge/config.py`) and the Docker dev loop work;
the HTTP gateway, upstream spawning, and auth middleware are not built yet — they are the open
tasks in `openspec/changes/mcp-bridge/tasks.md`.

## Spec-driven workflow (read this before changing behavior)

This project uses **OpenSpec**. The design source of truth is `openspec/changes/mcp-bridge/`
(`proposal.md` = why, `design.md` = how/decisions, `specs/*/spec.md` = requirements, `tasks.md` =
ordered work). Do not redesign ad hoc — read the relevant spec/design first, and implement against
`tasks.md`. Slash commands live in `.claude/commands/opsx/` (`/opsx:propose`, `/opsx:apply`, etc.).

```bash
openspec status --change mcp-bridge          # progress across artifacts
openspec instructions <artifact> --change mcp-bridge --json
```

## Commands

```bash
docker compose up                    # dev loop, gateway on :8000 (code is volume-mounted)
docker compose --profile tunnel up   # also opens the ngrok tunnel (inspector on :4040)
docker compose build                 # rebuild after pyproject dependency changes

python tests/test_config.py          # run the test suite (plain asserts, no pytest)
```

There is no lint step and no test framework — tests are framework-free `assert` self-checks run
directly with `python`. First-time setup: `cp .env.example .env` and `cp config.example.yaml config.yaml`.

## Conventions specific to this repo

- **Config split:** structure (upstreams, allowlist) lives in `config.yaml`; secrets
  (`BRIDGE_TOKEN`, `NGROK_AUTHTOKEN`) come from `.env` / environment only — never the YAML file.
- **Fail closed:** the bridge must refuse to start if `BRIDGE_TOKEN` is unset (see `Config.load`).
- **Allowlist is enforced twice:** filter `tools/list` *and* re-check on `tools/call` — hiding a
  tool is not refusing it (per `specs/access-control/spec.md`).
- **ngrok is a profiled compose service**, not baked into the Dockerfile; it stays out of the inner
  dev loop until you pass `--profile tunnel`.
- **Code is mounted, not installed editable:** edits on the host take effect on the next container
  run; `python -m bridge` picks up `/app`.
