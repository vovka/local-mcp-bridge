## ADDED Requirements

### Requirement: Run inside a Docker container
The gateway SHALL run as a single Docker container that starts the gateway and its configured
upstream MCP servers without manual setup on the host.

#### Scenario: Container starts the gateway
- **WHEN** the container is run with valid configuration
- **THEN** the gateway and its upstream servers start and the HTTP endpoint becomes reachable

### Requirement: Expose a public HTTPS endpoint via ngrok
The gateway SHALL open an ngrok HTTPS tunnel to its HTTP endpoint and SHALL surface the public
URL so it can be given to a cloud assistant.

#### Scenario: Public URL is available after startup
- **WHEN** the container starts with a valid ngrok auth token
- **THEN** an ngrok HTTPS tunnel points at the gateway and the public URL is logged

#### Scenario: Missing ngrok token
- **WHEN** no ngrok auth token is configured
- **THEN** startup fails with a clear error rather than serving only on localhost silently

### Requirement: Configure from a single config file and environment variables
The gateway SHALL read all settings — upstream servers, bearer token, tool allowlist, and ngrok
token — from environment variables and/or one config file, with no settings hard-coded.

#### Scenario: Configuration is loaded at startup
- **WHEN** the container starts
- **THEN** upstream servers, the bearer token, the allowlist, and the ngrok token are read from
  the config file / environment and applied
