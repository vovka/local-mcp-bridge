"""Bridge configuration: structure from a YAML file, secrets from env."""
import os
from dataclasses import dataclass, field

import yaml


@dataclass
class Upstream:
    name: str
    command: str
    args: list[str] = field(default_factory=list)


@dataclass
class Config:
    token: str
    upstreams: list[Upstream]
    allowlist: list[str]

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        token = os.environ.get("BRIDGE_TOKEN")
        if not token:  # fail closed: never serve an unauthenticated endpoint
            raise SystemExit("BRIDGE_TOKEN is required")
        data = _read_yaml(path or os.environ.get("CONFIG_PATH", "config.yaml"))
        return cls(token, _parse_upstreams(data), list(data.get("allowlist", [])))


def _read_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _parse_upstreams(data: dict) -> list[Upstream]:
    return [Upstream(**u) for u in data.get("upstreams", [])]
