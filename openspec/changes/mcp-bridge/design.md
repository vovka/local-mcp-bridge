## Context

Cloud assistants (Claude, ChatGPT) can attach to remote MCP servers over the **Streamable HTTP**
transport, but the tools worth attaching — browser automation, local files — run locally as
**stdio** MCP servers with no public address. We need a thin, self-hosted bridge: stdio upstream,
HTTP downstream, fronted by a public HTTPS URL, with auth and a tool allowlist as the only trust
boundary. Single user, their own laptop. Greenfield repo.

## Goals / Non-Goals

**Goals:**
- Re-expose selected local stdio MCP tools to a cloud assistant over one authenticated HTTPS URL.
- Fail closed: no token configured → no public service.
- Run as one `docker run` with config from a file + env secrets.

**Non-Goals:**
- Multi-user / OAuth / multi-tenant (single laptop owner only).
- A UI, persistence, or a tool marketplace.
- Rate limiting, audit logging, request quotas (note as future, not built now).
- Modifying or shipping the upstream MCP servers — they are consumed as-is.

## Decisions

**1. Official MCP Python SDK for the gateway.** It ships both a Streamable HTTP **server** and a
stdio **client** transport, so the bridge is glue, not protocol code.
- *Alternatives:* raw JSON-RPC (reinvents the transport — rejected); TypeScript SDK (equally fine;
  picked Python for brevity). Gateway language is independent of upstream language — upstreams are
  just spawned subprocesses.

**2. Streamable HTTP transport (not legacy SSE).** It is the transport current cloud assistants use
for remote MCP.

**3. Static bearer token, checked in ASGI middleware in front of the MCP app.** Simplest control
that holds the trust boundary for a single user.
- *ponytail ceiling:* static shared token. Upgrade path → OAuth if this ever serves more than one
  person. Token comes from env, never the config file, and startup aborts if unset.

**4. Allowlist enforced twice — filter `tools/list` AND re-check `tools/call`.** Hiding a tool is
not refusing it; both are required so a guessed tool name can't be invoked.

**5. ngrok agent as a sibling process; public URL read from its local API (`127.0.0.1:4040`).**
One binary, no extra SDK. Entry script starts ngrok, waits for the tunnel, logs the public URL,
then starts the gateway (which spawns the upstreams).
- *Alternative:* in-process ngrok SDK — more deps for no gain here.

**6. Config split: structure in one file, secrets in env.** `config.yaml` holds upstream server
commands + the tool allowlist; `BRIDGE_TOKEN` and `NGROK_AUTHTOKEN` come from env. Nothing
hard-coded.

**7. Serialize calls per upstream.** Browser-automation upstreams are single-session and stateful;
concurrent remote calls would interleave.
- *ponytail ceiling:* one lock per upstream process. Add per-session routing only if real
  concurrency is needed.

## Risks / Trade-offs

- **Public URL + token can drive the user's real laptop (e.g. their browser).** → The allowlist is
  the blast-radius control; document that allowlisted tools run with full laptop privileges. Token
  must be long/random; fail closed if missing.
- **ngrok free tier rotates the URL on each restart.** → Read and log the URL at runtime; user
  re-pastes it, or sets a reserved domain. Not our problem to solve in code.
- **Forwarded tool arguments are arbitrary.** → Gateway does not sanitize tool inputs; trust rests
  entirely on the allowlist choice. Stated explicitly so the user picks tools deliberately.
- **Upstream crash.** → Per spec, tool calls to a dead upstream return an MCP error; the public
  endpoint stays up. (Auto-restart of upstreams is a possible later add, not built now.)
- **Single gateway instance.** → Fine for one laptop; horizontal scaling is out of scope.

## Open Questions

- Should the entry script auto-restart a crashed upstream, or leave it dead until container
  restart? (Leaning: leave dead now, revisit if it bites.)
