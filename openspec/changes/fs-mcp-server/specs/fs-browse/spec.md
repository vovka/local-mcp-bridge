## ADDED Requirements

### Requirement: Configured root directory

The server SHALL be started with one base directory (its "root"). All tool paths are interpreted
relative to that root, and the root MUST exist and be a directory at startup.

#### Scenario: Root is missing

- **WHEN** the server starts with a root path that does not exist or is not a directory
- **THEN** the server exits with an error instead of serving requests

#### Scenario: Root provided

- **WHEN** the server starts with a valid root directory
- **THEN** it serves `list_dir` and `read_file` calls scoped to that root

### Requirement: List directory entries

The server SHALL expose a `list_dir` tool that, given a path inside the root, returns the entries
of that directory, each marked as a file or directory.

#### Scenario: List the root

- **WHEN** `list_dir` is called with the root (or an empty/`.` path)
- **THEN** it returns the names of the entries directly under the root, each tagged file vs directory

#### Scenario: Path is not a directory

- **WHEN** `list_dir` is called with a path that is a file or does not exist
- **THEN** it returns an MCP error rather than partial output

### Requirement: Read text file contents

The server SHALL expose a `read_file` tool that returns the contents of a file inside the root,
decoded as UTF-8 text.

#### Scenario: Read a file

- **WHEN** `read_file` is called with a path to a readable file under the root
- **THEN** it returns that file's text contents

#### Scenario: Target is not a file

- **WHEN** `read_file` is called with a path that is a directory or does not exist
- **THEN** it returns an MCP error

### Requirement: Path confinement

Every path SHALL be resolved (including following symlinks) and confined to the root. Any path that
resolves outside the root MUST be refused before any filesystem read of the target occurs.

#### Scenario: Parent-directory traversal

- **WHEN** a tool is called with a path containing `..` that would escape the root (e.g. `../../etc/passwd`)
- **THEN** the call is refused with an MCP error and nothing outside the root is read

#### Scenario: Absolute path outside root

- **WHEN** a tool is called with an absolute path that is not under the root
- **THEN** the call is refused with an MCP error

#### Scenario: Symlink escaping the root

- **WHEN** a path resolves through a symlink to a target outside the root
- **THEN** the call is refused with an MCP error

### Requirement: Read size cap

`read_file` SHALL cap the number of bytes it returns so a single call cannot return an unbounded
amount of data. When a file exceeds the cap, the response is truncated and marked as truncated.

#### Scenario: Oversized file

- **WHEN** `read_file` targets a file larger than the cap
- **THEN** the response contains at most the capped bytes and indicates the content was truncated

### Requirement: Read-only surface

The server SHALL expose no tool that creates, modifies, moves, or deletes filesystem entries. Only
read/browse operations are available.

#### Scenario: No mutation tools advertised

- **WHEN** a client lists the server's tools
- **THEN** the result contains only read/browse tools (e.g. `list_dir`, `read_file`) and no write, move, or delete tool
