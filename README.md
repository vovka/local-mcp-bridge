# local-mcp-bridge

Local-first gateway that exposes **selected** local MCP tools (e.g. browser automation) to
cloud AI assistants (Claude, ChatGPT) over one authenticated public HTTPS endpoint.

```
local stdio MCP servers ─▶ bridge (Streamable HTTP) ─▶ ngrok HTTPS ─▶ cloud assistant
```

A bearer token + a per-tool allowlist are the only trust boundary.

> **Status: scaffold.** The Docker dev loop and config loader work. The HTTP gateway itself is
> in progress — see `openspec/changes/mcp-bridge/tasks.md`.

## Run (Docker)

```bash
cp .env.example .env              # set BRIDGE_TOKEN to a long random value
cp config.example.yaml config.yaml

docker compose up                      # dev loop, gateway on :8000
docker compose --profile tunnel up     # also opens the ngrok HTTPS tunnel (inspector on :4040)
```

Code is volume-mounted into the container, so edits on the host take effect on the next run.

## Configuration

- `config.yaml` — upstream stdio MCP servers + the tool allowlist (structure).
- `.env` — `BRIDGE_TOKEN` (required), `NGROK_AUTHTOKEN` (tunnel only), `CONFIG_PATH` (optional).

Secrets live in `.env`, never in `config.yaml`. The bridge **fails to start without `BRIDGE_TOKEN`**.

## Security

The public URL + token can drive whatever tools you allowlist, **with your laptop's privileges**.
Allowlist deliberately and use a long, random `BRIDGE_TOKEN`.

## Tests

```bash
python tests/test_config.py       # config-loader self-check, no framework needed
```

## Design

Full proposal / design / specs / tasks: `openspec/changes/mcp-bridge/`.
