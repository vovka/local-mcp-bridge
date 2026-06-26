## 1. Project scaffold

- [ ] 1.1 Create Python project (pyproject) depending on the MCP SDK + a YAML parser
- [ ] 1.2 Add `config.example.yaml` (upstream server commands + tool allowlist) and document `BRIDGE_TOKEN` / `NGROK_AUTHTOKEN` env vars
- [ ] 1.3 Add a config loader: read file for structure, env for secrets; abort if `BRIDGE_TOKEN` unset (fail closed)

## 2. Upstream connection (mcp-gateway)

- [ ] 2.1 Spawn each configured upstream as a stdio MCP client session and run the initialize handshake
- [ ] 2.2 List each upstream's tools and build an aggregated tool map (tool name → owning upstream)
- [ ] 2.3 Serialize calls per upstream with a per-process lock
- [ ] 2.4 On upstream exit/error, mark its tools as failing (return MCP error) without tearing down the gateway

## 3. Public HTTP server (mcp-gateway)

- [ ] 3.1 Stand up an MCP Streamable HTTP server exposing the aggregated tools
- [ ] 3.2 Implement `tools/list` returning the (allowlisted) aggregated definitions
- [ ] 3.3 Implement `tools/call`: route to the owning upstream, forward args, return result/error; unknown tool → MCP error

## 4. Access control

- [ ] 4.1 Add ASGI bearer-token middleware in front of the MCP app; 401 on missing/wrong token, no upstream contact
- [ ] 4.2 Filter `tools/list` to the allowlist (hide everything else)
- [ ] 4.3 Re-check the allowlist in `tools/call`; refuse non-allowlisted tools before forwarding
- [ ] 4.4 Self-check (`test_*.py` or `__main__` asserts): wrong token → 401; non-allowlisted tool hidden in list AND refused on call

## 5. Deployment

- [ ] 5.1 Write Dockerfile bundling the gateway, the ngrok agent, and runtimes needed by the upstream servers
- [ ] 5.2 Entry script: start ngrok → poll `127.0.0.1:4040/api/tunnels` for the public HTTPS URL → log it → start the gateway; abort if `NGROK_AUTHTOKEN` unset
- [ ] 5.3 Verify end-to-end: `docker run` with example config, hit the ngrok URL with the token, list and call one allowlisted tool

## 6. Docs

- [ ] 6.1 README: config format, how to run, how to paste the ngrok URL + token into Claude/ChatGPT, and the security note (allowlisted tools run with full laptop privileges)
