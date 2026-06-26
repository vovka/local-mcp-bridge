## ADDED Requirements

### Requirement: Authenticate remote clients with a bearer token
The gateway SHALL require a bearer token on every request to the public endpoint and SHALL
reject any request whose token is missing or does not match the configured token.

#### Scenario: Valid token accepted
- **WHEN** a request arrives with `Authorization: Bearer <configured-token>`
- **THEN** the gateway processes the request

#### Scenario: Missing or wrong token rejected
- **WHEN** a request arrives with no token or an incorrect token
- **THEN** the gateway responds 401 and does not contact any upstream server

#### Scenario: No token configured
- **WHEN** the gateway starts without a configured bearer token
- **THEN** it refuses to start (fails closed) rather than serving an unauthenticated endpoint

### Requirement: Enforce a per-tool allowlist
The gateway SHALL expose only tools named in the configured allowlist; all other upstream tools
SHALL be hidden from listings and refused when called.

#### Scenario: Non-allowlisted tool hidden from listing
- **WHEN** an authenticated client lists tools
- **THEN** the response contains only allowlisted tools, even if upstream offers more

#### Scenario: Non-allowlisted tool call refused
- **WHEN** an authenticated client calls a tool that exists upstream but is not allowlisted
- **THEN** the gateway returns an error and does not forward the call upstream
